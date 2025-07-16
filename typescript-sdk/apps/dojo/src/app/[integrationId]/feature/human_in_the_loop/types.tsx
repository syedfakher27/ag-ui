// Position options
export type Position = "PG" | "SG" | "SF" | "PF" | "C";

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
  positionGap: Position;
  styleOfPlay: StyleOfPlay;
  developmentReadiness: DevelopmentReadiness;
  minutesPerGame: number;
  efficiencyRating: number;
  reboundBlockAssist: number;
  availability: AvailabilityStatus;
}

export interface FilterState {
  filters : TransferPortalFilters
}

// Example usage:


// Optional: Individual filter change handler types
export type FilterChangeHandler = (filterType: keyof TransferPortalFilters, value: any) => void;
export type AvailabilityChangeHandler = (key: keyof AvailabilityStatus, checked: boolean) => void;