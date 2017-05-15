import pandas as pd
import numpy as np
from itertools import combinations
total_overs = 20
teams = ['DD','GL','KKR','RPS','KXIP','RCB','SRH','MI']


def count_balls (overs):
    no_of_overs = int(overs)
    b = overs - no_of_overs
    balls = round((b*10),0)
    total_balls = no_of_overs * 6 + balls
    return total_balls


def pre_alterations(matches):

    matches['1st_balls'] = matches['1st_overs']
    matches['2nd_balls'] = matches['2nd_overs']
    for i, record in matches.iterrows():
        matches.loc[i, '1st_balls'] = total_overs * 6
        if record['ball_first'] == record['winner']:
            matches.loc[i, '2nd_balls'] = count_balls(record['2nd_overs'])
        else:
            matches.loc[i, '2nd_balls'] = total_overs * 6

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
    points_table.index = points_table['team']
    return points_table


def get_combinations(matches_list):
    all_combinations = []
    for i in range(len(matches_list)):
        comb = combinations(matches_list, i + 1)
        for i in list(comb):
            all_combinations.append(i)
    return list(all_combinations)

def run():
    # match_file_name = "ipl17.xlsx"
    # matches = pd.read_excel(match_file_name, sheet_name="Compact", index_col="match")
    # matches = pre_alterations(matches)
    # print(get_points_table(matches))
    print (get_combinations(['1',2,['a','b','b']]))

if __name__ == '__main__':
    run()
