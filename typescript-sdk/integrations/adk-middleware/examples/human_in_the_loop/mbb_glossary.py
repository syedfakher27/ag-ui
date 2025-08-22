mbb_metrics="""Basket Ball Player Rating and Metrics Glossary:

OBPR: Offensive Bayesian Performance Rating reflects the offensive value a player brings to his team when he is on the court. This rating incorporates a player’s individual efficiency stats and on-court play-by-play impact, and also accounts for the offensive strength of other teammates on the floor with him, along with the defensive strength of the opponent’s players on the floor. OBPR is interpreted as the number of offensive points per 100 possessions above D1 average expected by the player’s team if the player were on the court with 9 other average players. A higher rating is better.
DBPR: Defensive Bayesian Performance Rating reflects the defensive value a player brings to his team when he is on the court. This rating incorporates a player’s individual efficiency stats and on-court play-by-play impact, and also accounts for the defensive strength of other teammates on the floor with him, along with the offensive strength of the opponent’s players on the floor. DBPR is interpreted as the number of defensive points per 100 possessions better than (below) D1 average expected to be allowed by the player’s team if the player were on the court with 9 other average players. A higher rating is better.
BPR: Bayesian Performance Rating is the sum of a player’s OBPR and DBPR. This rating is the ultimate measure of a player’s overall value to his team when he is on the floor. BPR is interpreted as the number of points per 100 possessions better than the opponent the player’s team is expected to be if the player were on the court with 9 other average players. A higher rating is better.
Change: Improvement in BPR over the last 30 days.
Off Poss: Number of offensive possessions played.
Def Poss: Number of defensive possessions played.
Box OBPR: Box Offensive Bayesian Performance Rating is an estimate of a player’s offensive value, based only on his individual box stats. This serves as a prior starting point when calculating OBPR.
Box DBPR: Box Defensive Bayesian Performance Rating is an estimate of a player’s defensive value, based only on his individual box stats. This serves as a prior starting point when calculating DBPR.
Box BPR: Box Bayesian Performance Rating is the sum of a player’s Box OBPR and Box DBPR. This rating is an estimate of a player’s overall value, based only on his individual box stats.
Adj Team Off Eff: Team offensive efficiency (points scored per 100 possessions) with player on the court, adjusted for strength of opponent players faced. A higher value is better.
Adj Team Def Eff: Team defensive efficiency (points allowed by opponent per 100 possessions) with player on the court, adjusted for strength of opponent players faced. A lower value is better.
Adj Team Eff Margin: Difference between adjusted team offensive and adjusted defensive efficiency with player on the court. A higher value is better.
+/-: Number of points scored for the player’s team with him on the court, minus the number of points scored by the opponent with him on the court.
Position: An estimate of a player’s position based on his individual stats and team contributions. An estimated position of 1 corresponds to being a point guard, and a 5 corresponds to being a center. This estimate comes from Daniel Myers’ Box Plus Minus 2.0.
Role: An estimate of a player’s offensive role based on his individual stats and team contributions. An estimated role of 1 corresponds to being the “creator” in the offense, and a 5 corresponds to being the “receiver”. This estimate comes from Daniel Myers’ Box Plus Minus 2.0.

3PT%: A player’s predicted three-point shooting percentage against an average opponent, adjusted for usage.
2PT%: A player’s predicted two-point shooting percentage against an average opponent, adjusted for usage.
FT%: A player’s predicted free throw shooting percentage against an average opponent.
Scoring Volume: A player’s predicted points per 100 possessions based on predicted shot usage and efficiency.
Assist Rate: A player’s predicted assist rate against an average opponent, adjusted for usage. Assist Rate is the percentage of teammate made field goals that the player assisted while on the court.
Turnover %: A player’s predicted turnover percentage against an average opponent, adjusted for usage. Turnover percentage is the percentage of offensive possessions that end in the player turning the ball over while on the court.
Playmaking Score: A player’s predicted playmaking score, which combines predicted assist rate and turnover rate to measure a player’s ability to create plays for others with the ball in his hands.
O-Reb %: A player’s predicted offensive rebound percentage against an average opponent, adjusted for usage. Offensive rebound percentage is the percentage of possible offensive rebounds that the player secured while on the court.
D-Reb %: A player’s predicted defensive rebound percentage against an average opponent, adjusted for usage. Defensive rebound percentage is the percentage of possible defensive rebounds that the player secured while on the court.
Rebounding %: A player’s predicted offensive + defensive rebounding rate. See O-Reb % and D-Reb % for more detail.
Steal %: A player’s predicted steal percentage against an average opponent. Steal percentage is percentage of defensive possessions that end in the player stealing the ball while on the court.
Block %: A player’s predicted block percentage against an average opponent, adjusted for usage.. Block percentage is the percentage of opponent two-point field goal attempts that the player blocked while on the court.
Foul %: A player’s predicted personal fouls committed per 100 possessions.
Defensive Value: A player’s defensive per-possession value to a team, against an average opponent, as measured by Defensive BPR. DBPR reflects the defensive value a player brings to his team when he is on the court.
"""