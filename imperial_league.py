import pandas as pd
import numpy as np
import random as rd
import os

def load_team_data(file_path):
    return pd.read_csv(file_path, encoding='latin1')

def simulate_match(home_skills, away_skills):
    atk1, def1 = home_skills["ATK"], home_skills["DEF"]
    atk2, def2 = away_skills["ATK"], away_skills["DEF"]

    home_boost = 1.05
    atk1 *= home_boost
    def1 *= home_boost

    atk1, def1 = np.clip(atk1, 1, 99), np.clip(def1, 1, 99)
    atk2, def2 = np.clip(atk2, 1, 99), np.clip(def2, 1, 99)

    atk_factor1 = atk1 / (def2 + 20)
    atk_factor2 = atk2 / (def1 + 20)

    base_mean1 = atk_factor1 * 1.8
    base_mean2 = atk_factor2 * 1.7

    mean1 = np.clip(np.random.laplace(base_mean1 + 0.2, 0.15), 0.4, 5.5)
    mean2 = np.clip(np.random.laplace(base_mean2 + 0.2, 0.15), 0.4, 5.2)

    score1 = np.random.poisson(mean1)
    score2 = np.random.poisson(mean2)

    if score1 == 0 and mean1 > 1.9:
        score1 = 1
    if score2 == 0 and mean2 > 1.9:
        score2 = 1

    if abs(score1 - score2) == 1 and np.random.rand() < 0.025:
        score2 = score1

    if score1 == 0 and score2 == 0 and np.random.rand() < 0.7:
        score1 = score2 = 1

    return score1, score2

def update_results(results, team, gf, ga):
    results[team]["P"] += 1
    results[team]["GF"] += gf
    results[team]["GA"] += ga
    results[team]["GD"] += gf - ga

    if gf > ga:
        results[team]["W"] += 1
        results[team]["Points"] += 3
    elif gf == ga:
        results[team]["D"] += 1
        results[team]["Points"] += 1
    else:
        results[team]["L"] += 1

def init_results(teams):
    return {team: {"P": 0, "W": 0, "D": 0, "L": 0,
                   "GF": 0, "GA": 0, "GD": 0, "Points": 0}
            for team in teams}

def simulate_division_matches(division_teams, teams_data):
    results = init_results(division_teams)
    match_log = []

    for i, team1 in enumerate(division_teams):
        for team2 in division_teams[i+1:]:
            skills1 = teams_data.loc[teams_data["Team"] == team1, ["ATK", "DEF"]].iloc[0]
            skills2 = teams_data.loc[teams_data["Team"] == team2, ["ATK", "DEF"]].iloc[0]

            score1, score2 = simulate_match(skills1, skills2)
            match_log.append({"Team 1": team1, "Score 1": score1, "Score 2": score2, "Team 2": team2})
            update_results(results, team1, score1, score2)
            update_results(results, team2, score2, score1)

            score1, score2 = simulate_match(skills2, skills1)
            match_log.append({"Team 1": team2, "Score 1": score1, "Score 2": score2, "Team 2": team1})
            update_results(results, team2, score1, score2)
            update_results(results, team1, score2, score1)

    return results, match_log

def simulate_interdivisional_matches(teams_by_division, teams_data):
    all_teams = [team for division in teams_by_division.values() for team in division]
    results = init_results(all_teams)
    match_log = []

    divisions = list(teams_by_division.keys())

    for i in range(len(divisions)):
        for j in range(i+1, len(divisions)):
            teamsA = sorted(teams_by_division[divisions[i]])
            teamsB = sorted(teams_by_division[divisions[j]])

            for m, teamA in enumerate(teamsA):
                for n, teamB in enumerate(teamsB):
                    if (m + n) % 2 == 0:
                        home, away = teamA, teamB
                    else:
                        home, away = teamB, teamA

                    skills_home = teams_data.loc[teams_data["Team"] == home, ["ATK", "DEF"]].iloc[0]
                    skills_away = teams_data.loc[teams_data["Team"] == away, ["ATK", "DEF"]].iloc[0]

                    score1, score2 = simulate_match(skills_home, skills_away)
                    match_log.append({"Team 1": home, "Score 1": score1, "Score 2": score2, "Team 2": away})

                    update_results(results, home, score1, score2)
                    update_results(results, away, score2, score1)

    return results, match_log

def assign_seeds_to_teams(final_results):
    import pandas as pd

    champions_list = []
    last_place_list = []
    others_list = []
    for division, df in final_results.items():
        division_sorted = df.sort_values(by=["Points", "GD", "GF"], ascending=[False, False, False])
        champions_list.append(division_sorted.iloc[[0]])      
        last_place_list.append(division_sorted.iloc[[-1]])    
        others_list.append(division_sorted.iloc[1:-1])          

    champions_df = pd.concat(champions_list).copy()
    last_place_df = pd.concat(last_place_list).copy()
    others_df = pd.concat(others_list).copy()

    champions_sorted = champions_df.sort_values(by=["Points", "GD", "GF"], ascending=[False, False, False]).copy()
    last_place_sorted = last_place_df.sort_values(by=["Points", "GD", "GF"], ascending=[False, False, False]).copy()
    others_sorted = others_df.sort_values(by=["Points", "GD", "GF"], ascending=[False, False, False]).copy()

    champions_sorted["Seed"] = range(1, 5)                    
    others_sorted["Seed"] = range(5, 5 + len(others_sorted))   
    last_place_sorted["Seed"] = range(29, 33)                 

    all_teams = pd.concat([champions_sorted, others_sorted, last_place_sorted])
    all_teams = all_teams.sort_values("Seed").copy()

    return all_teams["Seed"]

def penalty_shootout(higher, lower, p_high=0.85, p_low=0.80):
    high_score = low_score = 0

    for i in range(5):
        high_score += rd.random() < p_high
        low_score += rd.random() < p_low

    while high_score == low_score:
        high_hit = rd.random() < p_high
        low_hit = rd.random() < p_low

        if high_hit != low_hit:
            return higher if high_hit else lower

    return higher if high_score > low_score else lower

def postseason_tiebreaker(seed1, seed2, team1, team2):
    higher, lower = (team1, team2) if seed1 < seed2 else (team2, team1)
    winner = penalty_shootout(higher, lower)
    return (winner, seed1 if winner == team1 else seed2)

def simulate_postseason_match(team1, seed1, team2, seed2, team_skills):
    skills1 = team_skills[team1].copy()
    skills2 = team_skills[team2].copy()

    seed_diff = abs(seed2 - seed1)

    if seed_diff > 2:
        bonus_per_seed = 0.05 
        max_bonus = 0.25     

        bonus_value = min(seed_diff * bonus_per_seed, max_bonus)

        if seed1 < seed2:
            skills1["ATK"] += bonus_value
            skills1["DEF"] += bonus_value
        else:
            skills2["ATK"] += bonus_value
            skills2["DEF"] += bonus_value

    score1, score2 = simulate_match(skills1, skills2)

    if score1 > score2:
        return team1, seed1
    elif score2 > score1:
        return team2, seed2
    else:

        def penalty_shootout(higher, lower, p_high=0.85, p_low=0.80):
            high_score = low_score = 0

            for i in range(5):
                high_score += rd.random() < p_high
                low_score += rd.random() < p_low

            while high_score == low_score:
                high_hit = rd.random() < p_high
                low_hit = rd.random() < p_low

                if high_hit != low_hit:
                    return higher if high_hit else lower

            return higher if high_score > low_score else lower

        def postseason_tiebreaker(seed1, seed2, team1, team2):
            higher, lower = (team1, team2) if seed1 < seed2 else (team2, team1)
            winner = penalty_shootout(higher, lower)
            return (winner, seed1 if winner == team1 else seed2)
        
        return postseason_tiebreaker(seed1, seed2, team1, team2)

def postseason(general_table, teams_data):
    match_results = []

    top_12 = general_table.nsmallest(12, "Seed").copy()
    top_12 = top_12.set_index("Seed")

    team_skills = {
        row["Team"]: {"ATK": row["ATK"], "DEF": row["DEF"]}
        for _, row in teams_data.iterrows()
    }

    elimination_seeds = sorted(top_12.loc[5:12].index)
    advancing = []

    for i in range(4):
        high = elimination_seeds.pop(0)
        low = elimination_seeds.pop(-1)

        team_high = top_12.loc[high]["Team"]
        team_low = top_12.loc[low]["Team"]

        winner, winner_seed = simulate_postseason_match(team_high, high, team_low, low, team_skills)

        match_results.append({
            "Round": "Eliminations",
            "Match": f"E{i+1}",
            "Higher Seed": high,
            "Contender": team_high,
            "Lower Seed": low,
            "Opponent": team_low,
            "Winner": winner
        })

        advancing.append(winner_seed)

    quarterfinal_seeds = sorted(advancing + [1, 2, 3, 4])

    def simulate_round(seeds_list, round_name, prefix):
        seeds = sorted(seeds_list)
        winners = []

        for i in range(len(seeds) // 2):
            high = seeds.pop(0)
            low = seeds.pop(-1)

            team_high = top_12.loc[high]["Team"]
            team_low = top_12.loc[low]["Team"]

            winner, winner_seed = simulate_postseason_match(team_high, high, team_low, low, team_skills)

            match_results.append({
                "Round": round_name,
                "Match": f"{prefix}{i+1}" if prefix != "F" else "F",
                "Higher Seed": high,
                "Contender": team_high,
                "Lower Seed": low,
                "Opponent": team_low,
                "Winner": winner
            })

            winners.append(winner_seed)

        return winners

    semifinalists = simulate_round(quarterfinal_seeds, "Quarterfinals", "Q")
    finalists = simulate_round(semifinalists, "Semifinals", "S")
    champion = simulate_round(finalists, "Final", "F")

    return pd.DataFrame(match_results)

def save_results_to_excel(final_results, match_log, team_data):
    try:
        output_file = "imperial_league_results.xlsx"
        all_teams = []

        for division, df in final_results.items():
            df_copy = df.copy()
            df_copy["Division"] = division
            df_copy["Team"] = df_copy.index

            df_sorted = df_copy.sort_values(by=["Points", "GD", "GF"], ascending=[False, False, False]).copy()
            df_sorted["Place"] = range(1, len(df_sorted) + 1)

            all_teams.append(df_sorted)

        general_table = pd.concat(all_teams, ignore_index=True)

        seeds = assign_seeds_to_teams(final_results).rename("Seed")
        general_table = general_table.set_index("Team").join(seeds, how="left").reset_index()

        general_table.rename(columns={"Points": "PTS"}, inplace=True)
        general_table = general_table[["Division", "Seed", "Place", "Team", "W", "D", "L", "GF", "GA", "GD", "PTS"]]
        general_table = general_table.sort_values("Seed").reset_index(drop=True)

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            general_table.to_excel(writer, sheet_name="General Table", index=False)

            for division in final_results.keys():
                division_df = general_table[general_table["Division"] == division].copy()
                division_df = division_df.sort_values("Place")
                division_df.to_excel(writer, sheet_name=division, index=False)

            pd.DataFrame(match_log).to_excel(writer, sheet_name="Match Log", index=False)
            postseason(general_table, team_data).to_excel(writer, sheet_name="Postseason", index=False)

        print(f"League simulation complete. Results saved to {output_file}")

    except Exception as e:
        print(f"Error saving to Excel: {e}")

def simulate_league():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "imperial_league_skills.csv")
    team_data = load_team_data(file_path)

    teams_by_division = {
        "Eastern": team_data[team_data["Division"] == "Eastern"]["Team"].tolist(),
        "Northern": team_data[team_data["Division"] == "Northern"]["Team"].tolist(),
        "Western": team_data[team_data["Division"] == "Western"]["Team"].tolist(),
        "Southern": team_data[team_data["Division"] == "Southern"]["Team"].tolist(),
    }

    division_results = {}
    match_log = []
    for division, teams in teams_by_division.items():
        division_results[division], division_log = simulate_division_matches(teams, team_data)
        match_log.extend(division_log)

    results_interdivisional, inter_log = simulate_interdivisional_matches(teams_by_division, team_data)
    match_log.extend(inter_log)

    final_results = {}
    for division, teams in teams_by_division.items():
        combined_results = division_results[division]
        for team in combined_results:
            inter_results = results_interdivisional[team]
            for key in ["P", "W", "D", "L", "GF", "GA", "GD", "Points"]:
                combined_results[team][key] += inter_results[key]
        final_results[division] = pd.DataFrame.from_dict(combined_results, orient="index")

    save_results_to_excel(final_results, match_log, team_data)

simulate_league()