// Position options
export type Position = "PG" | "SG" | "SF" | "PF" | "C";
// Class options
export type Class = "FR" | "SO" | "JR" | "SR";
// Team options
export const TEAM_OPTIONS = [
  "Abilene Christian", "Air Force", "Akron", "Alabama", "Alabama A&M", "Alabama State", 
  "Albany", "Alcorn State", "Appalachian State", "Arizona", "Arizona State", "Arkansas", 
  "Arkansas State", "Arkansas-Little Rock", "Arkansas-Pine Bluff", "Army", "Auburn", 
  "Austin Peay", "BYU", "Ball State", "Baylor", "Bellarmine", "Belmont", "Bethune-Cookman", 
  "Binghamton", "Boise State", "Boston College", "Bowling Green", "Bradley", "Brown", 
  "Bryant", "Bucknell", "Buffalo", "Butler", "Cal Poly", "Cal State Bakersfield", 
  "Cal State Fullerton", "Cal State Northridge", "California", "California Baptist", 
  "Campbell", "Canisius", "Central Arkansas", "Central Connecticut", "Central Michigan", 
  "Charleston", "Charlotte", "Chattanooga", "Chicago State", "Cincinnati", "Citadel", 
  "Clemson", "Cleveland State", "Coastal Carolina", "Colgate", "Colorado", "Colorado State", 
  "Columbia", "Connecticut", "Coppin State", "Cornell", "Creighton", "Dartmouth", 
  "Davidson", "Dayton", "Delaware", "Delaware State", "Denver", "DePaul", "Detroit Mercy", 
  "Drake", "Drexel", "Duke", "Duquesne", "East Carolina", "East Tennessee State", 
  "Eastern Illinois", "Eastern Kentucky", "Eastern Michigan", "Eastern Washington", 
  "Elon", "Evansville", "Fairfield", "Fairleigh Dickinson", "Florida", "Florida A&M", 
  "Florida Atlantic", "Florida Gulf Coast", "Florida International", "Florida State", 
  "Fordham", "Fresno State", "Furman", "Gardner-Webb", "George Mason", "George Washington", 
  "Georgetown", "Georgia", "Georgia Southern", "Georgia State", "Georgia Tech", 
  "Gonzaga", "Grambling State", "Grand Canyon", "Green Bay", "Hampton", "Hartford", 
  "Harvard", "Hawaii", "High Point", "Hofstra", "Holy Cross", "Houston", "Houston Christian", 
  "Howard", "Idaho", "Idaho State", "Illinois", "Illinois State", "Indiana", "Indiana State", 
  "Iona", "Iowa", "Iowa State", "IUPUI", "Jackson State", "Jacksonville", "Jacksonville State", 
  "James Madison", "Kansas", "Kansas State", "Kennesaw State", "Kent State", "Kentucky", 
  "La Salle", "Lafayette", "Lamar", "Le Moyne", "Lehigh", "Liberty", "Lindenwood", 
  "Lipscomb", "Long Beach State", "Long Island", "Longwood", "Louisiana", "Louisiana Monroe", 
  "Louisiana Tech", "Louisville", "Loyola (IL)", "Loyola (MD)", "Loyola Marymount", 
  "LSU", "Maine", "Manhattan", "Marist", "Marquette", "Marshall", "Maryland", 
  "Maryland Eastern Shore", "Massachusetts", "McNeese State", "Memphis", "Mercer", 
  "Miami", "Miami (OH)", "Michigan", "Michigan State", "Middle Tennessee", "Milwaukee", 
  "Minnesota", "Mississippi", "Mississippi State", "Mississippi Valley State", 
  "Missouri", "Missouri State", "Monmouth", "Montana", "Montana State", "Morehead State", 
  "Morgan State", "Mount St. Mary's", "Murray State", "Navy", "NC State", "Nebraska", 
  "Nevada", "New Hampshire", "New Mexico", "New Mexico State", "New Orleans", "Niagara", 
  "Nicholls State", "Norfolk State", "North Alabama", "North Carolina", "North Carolina A&T", 
  "North Carolina Central", "North Dakota", "North Dakota State", "North Florida", 
  "North Texas", "Northeastern", "Northern Arizona", "Northern Colorado", "Northern Illinois", 
  "Northern Iowa", "Northern Kentucky", "Northwestern", "Northwestern State", "Notre Dame", 
  "Oakland", "Ohio", "Ohio State", "Oklahoma", "Oklahoma State", "Old Dominion", 
  "Oral Roberts", "Oregon", "Oregon State", "Pacific", "Penn State", "Pennsylvania", 
  "Pepperdine", "Pittsburgh", "Portland", "Portland State", "Prairie View A&M", 
  "Presbyterian", "Princeton", "Providence", "Purdue", "Purdue Fort Wayne", "Quinnipiac", 
  "Radford", "Rhode Island", "Rice", "Richmond", "Rider", "Robert Morris", "Rutgers", 
  "Sacramento State", "Sacred Heart", "Saint Francis", "Saint Joseph's", "Saint Louis", 
  "Saint Mary's", "Saint Peter's", "Sam Houston State", "Samford", "San Diego", 
  "San Diego State", "San Francisco", "San Jose State", "Santa Clara", "Seattle", 
  "Seton Hall", "Siena", "South Alabama", "South Carolina", "South Carolina State", 
  "South Carolina Upstate", "South Dakota", "South Dakota State", "South Florida", 
  "Southeast Missouri State", "Southeastern Louisiana", "Southern", "Southern California", 
  "Southern Illinois", "Southern Miss", "Southern Utah", "St. Bonaventure", "St. John's", 
  "Stanford", "Stephen F. Austin", "Stetson", "Stony Brook", "Syracuse", "Tarleton State", 
  "TCU", "Temple", "Tennessee", "Tennessee Martin", "Tennessee State", "Tennessee Tech", 
  "Texas", "Texas A&M", "Texas A&M Commerce", "Texas Southern", "Texas State", "Texas Tech", 
  "Toledo", "Towson", "Troy", "Tulane", "Tulsa", "UAB", "UC Davis", "UC Irvine", 
  "UC Riverside", "UC San Diego", "UC Santa Barbara", "UCF", "UCLA", "UIC", "UMBC", 
  "UMKC", "UNC Asheville", "UNC Charlotte", "UNC Greensboro", "UNC Wilmington", 
  "UNLV", "USC", "Utah", "Utah State", "Utah Tech", "Utah Valley", "UTEP", 
  "UT Martin", "UTSA", "Valparaiso", "Vanderbilt", "VCU", "Vermont", "Villanova", 
  "Virginia", "Virginia Tech", "VMI", "Wagner", "Wake Forest", "Washington", 
  "Washington State", "Weber State", "West Virginia", "Western Carolina", "Western Illinois", 
  "Western Kentucky", "Western Michigan", "Wichita State", "William & Mary", "Winthrop", 
  "Wisconsin", "Wofford", "Wright State", "Wyoming", "Xavier", "Yale", "Youngstown State"
] as const;

// Team type derived from the constant
export type Team = typeof TEAM_OPTIONS[number] | "";

// Style of play options
export type StyleOfPlay = 
  | "Transition offense"
  | "Half-court offense"
  | "Defense-first"
  | "Balanced";

// Development readiness options
export type DevelopmentReadiness = 
  | "Immediate impact"
  | "Multi-year potential"
  | "Project player";

// Range type for sliders (min, max)
export type Range = [number, number];

// Availability status object
export interface AvailabilityStatus {
  stillAvailable: boolean;
  committed: boolean;
  draftBound: boolean;
}

// Main filters interface
export interface TransferPortalFilters {
  // positionGap: Position;
  // // styleOfPlay: StyleOfPlay;
  // // developmentReadiness: DevelopmentReadiness;
  // // minutesPerGame: number;
  // efficiencyRating: number;
  // team: Team;
  // class_: Class;
  excludeCommitted: boolean;
  // reboundBlockAssist: number;
  // availability: AvailabilityStatus;
}

export interface FilterState {
  filters : TransferPortalFilters
}

// Example usage:


// Optional: Individual filter change handler types
export type FilterChangeHandler = (filterType: keyof TransferPortalFilters, value: any) => void;
export type AvailabilityChangeHandler = (key: keyof AvailabilityStatus, checked: boolean) => void;