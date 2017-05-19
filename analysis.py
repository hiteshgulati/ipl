import pandas as pd
import numpy as np
from itertools import combinations
total_overs = 20
teams = ['DD','GL','KKR','RPS','KXIP','RCB','SRH','MI']


def count_balls(overs):
    no_of_overs = int(overs)
    b = overs - no_of_overs
    balls = round((b*10),0)
    total_balls = no_of_overs * 6 + balls
    return total_balls


def pre_alterations(matches):
    matches['1st_balls'] = matches['1st_overs']
    matches['2nd_balls'] = matches['2nd_overs']
    matches['looser'] = matches ['bat_first']
    for i, record in matches.iterrows():
        matches.loc[i, '1st_balls'] = total_overs * 6
        if record['ball_first'] == record['winner']:
            matches.loc[i, '2nd_balls'] = count_balls(record['2nd_overs'])
        else:
            matches.loc[i, '2nd_balls'] = total_overs * 6
        if record['bat_first'] == record['winner']:
            matches.loc[i, 'looser'] = record['ball_first']
        elif record['ball_first'] == record['winner']:
            matches.loc[i, 'looser'] = record['bat_first']
        else:
            matches.loc[i, 'looser'] = 'NA'
    return matches


def get_points_table(matches):
    team_record = dict(team=0, played=0, won=0, points=0, for_runs=0, for_balls=0, for_rr=0,
                       against_runs=0, against_balls=0, against_rr=0, nrr=0)
    points_table = pd.DataFrame(data=None, columns=list(team_record))
    for item in teams:
        team_record = dict(team=0, played=0, won=0, points=0, for_runs=0, for_balls=0, for_rr=0,
                           against_runs=0, against_balls=0, against_rr=0, nrr=0)
        team_record['team']= item
        for i, record in matches.iterrows():
            if record['bat_first'] == item or record['ball_first'] == item:
                team_record['played'] += 1
                if record['winner'] == item:
                    team_record['won'] += 1
                    team_record['points'] += 2
                elif record['result?'] == 'N':
                    team_record['points'] += 1
                if record['bat_first'] == item:
                    team_record['for_runs'] += record['1st_runs']
                    team_record['for_balls'] += record['1st_balls']
                    team_record['against_runs'] += record['2nd_runs']
                    team_record['against_balls'] += record['2nd_balls']
                elif record['ball_first'] == item:
                    team_record['for_runs'] += record['2nd_runs']
                    team_record['for_balls'] += record['2nd_balls']
                    team_record['against_runs'] += record['1st_runs']
                    team_record['against_balls'] += record['1st_balls']
        team_record['for_rr'] = team_record['for_runs']/team_record['for_balls']
        team_record['against_rr'] = team_record['against_runs']/team_record['against_balls']
        team_record['nrr'] = (team_record['for_rr']-team_record['against_rr'])*6
        points_table = points_table.append(team_record,ignore_index=True)
    points_table.sort_values(by=['points','nrr'], ascending=False, axis=0, inplace=True)
    points_table.reset_index(inplace=True)
    points_table['index'] = points_table.index
    return points_table


def get_combinations(matches_list):
    all_combinations = []
    for i in range(len(matches_list)):
        comb = combinations(matches_list, i + 1)
        for i in list(comb):
            all_combinations.append(list(i))
    return list(all_combinations)


def get_matches_list(team,matches):
    matches_list = []
    for i, record in matches.iterrows():
        if team == record['looser']:
            matches_list.append(record['match'])
    return matches_list


def is_success (team,matches):
    points_table = get_points_table(matches)
    flag = False
    rank = int(points_table[points_table.team == team]['index'])
    if rank <= 3:
        flag = True
    elif rank > 3:
        flag = False
    return flag


def is_equalized(team,matches):
    points_table = get_points_table(matches)
    flag = False
    points_team = int(points_table[points_table.team == team]['points'])
    points_rank3 = int(points_table.loc[3]['points'])
    if points_team == points_rank3:
        flag = True
    return flag


def get_avg_runrate (team,matches):
    points_table = get_points_table(matches)
    avg_runrate = points_table[points_table.team == team]['for_rr']
    return float(avg_runrate)


def runs_to_topple(team,altered_matches):
    points_table = get_points_table(altered_matches)
    against_team = str(points_table.loc[3]['team'])
    topple_runs = 0
    upper_runs_limit = (((float(points_table[points_table.team == against_team]['nrr']) -
                         float(points_table[points_table.team == team]['nrr'])) *
                        float(points_table[points_table.team == against_team]['for_balls']))/6)+1
    for i, record in altered_matches.iterrows():
        if record['bat_first'] == team or record['bat_first'] == against_team:
            if record['ball_first'] == against_team or record['ball_first'] == team:
                for j in range(round(upper_runs_limit)):
                    if record['bat_first'] == team and record['ball_first'] == against_team:
                        altered_matches['1st_runs'].loc[i] += j
                    if record['ball_first'] == team and record['bat_first'] == against_team:
                        altered_matches['2nd_runs'].loc[i] += j
                    if is_success(team,altered_matches):
                        topple_runs = j
                        break
                break
    return topple_runs,altered_matches


def examine_combinations(all_combinations,team,matches):
    combination_record = dict(combination=[], runs=0, success=False)
    combination_table = pd.DataFrame(data=None, columns=list(combination_record))
    for i in all_combinations:
        combination_record = dict(combination=i, runs=0, success=False)
        altered_matches = matches.copy()
        for j in i:
            if matches.loc[j-1]['ball_first'] == team:
                run_difference = altered_matches.loc[j-1]['1st_runs'] - altered_matches.loc[j-1]['2nd_runs'] + 1
                altered_matches['2nd_runs'].loc[j - 1] += run_difference
                combination_record['runs'] += run_difference
            if matches.loc[j-1]['bat_first'] == team:
                ball_difference = 120 - matches.loc[j-1]['2nd_balls']
                avg_runrate = get_avg_runrate(matches.loc[j-1]['ball_first'],matches)
                match_runrate = matches.loc[j-1]['2nd_runs']/matches.loc[j-1]['2nd_balls']
                if avg_runrate > match_runrate:
                    added_runs = round(avg_runrate*ball_difference)
                else:
                    added_runs = round(match_runrate * ball_difference)
                altered_matches['2nd_runs'].loc[j - 1] += added_runs
                run_difference = altered_matches.loc[j - 1]['2nd_runs'] - altered_matches.loc[j - 1]['1st_runs'] + 1
                altered_matches['1st_runs'].loc[j - 1] += run_difference
                combination_record['runs'] += run_difference
            altered_matches['winner'].loc[j - 1] = team
        if not is_success(team,altered_matches):
            if is_equalized(team,altered_matches):
                while not is_success(team,altered_matches):
                    topple_runs, altered_matches = runs_to_topple(team,altered_matches)
                    combination_record['runs'] += topple_runs
        combination_record['success'] = is_success(team,altered_matches)
        combination_table = combination_table.append(combination_record,ignore_index=True)
    return combination_table


def run():
    match_file_name = "ipl17.xlsx"
    matches = pd.read_excel(match_file_name, sheet_name="Compact")
    matches = pre_alterations(matches)
    # team_record = dict(name='', runs = 0)
    # team_runs_slippage = pd.DataFrame(data=None, columns=list(team_record))
    # team_list = ['DD','KXIP','GL','RCB']
    # for team in team_list:
    #     all_combinations = get_combinations(get_matches_list(team, matches))
    #     print(team, all_combinations)
    #     combination_table = examine_combinations(all_combinations,team,matches)
    #     successful_combinations = combination_table[combination_table.success == True]
    #     successful_combinations.sort_values(by=['runs'], axis=0, inplace=True)
    #     successful_combinations.reset_index(inplace=True)
    #     successful_combinations['rank'] = successful_combinations.index
    #     team_record['name'] = team
    #     team_record['runs'] = successful_combinations.loc[0]['runs']
    #     team_runs_slippage = team_runs_slippage.append(team_record,ignore_index=True)
    #     print(team_record)
    # team_runs_slippage.to_excel("runs_slippage.xlsx")
    # print(team_runs_slippage)
    print(count_balls(0))
    # print(get_points_table(matches))


if __name__ == '__main__':
    run()
