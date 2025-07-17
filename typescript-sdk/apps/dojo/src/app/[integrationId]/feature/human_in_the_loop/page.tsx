"use client";
import React, { useState, useEffect } from "react";
import "@copilotkit/react-ui/styles.css";
import "./style.css";
import { CopilotKit, useCopilotAction, useLangGraphInterrupt, useCoAgent } from "@copilotkit/react-core";
import { FilterState, FilterChangeHandler, AvailabilityChangeHandler, TEAM_OPTIONS } from './types';
import { CopilotChat } from "@copilotkit/react-ui";

interface HumanInTheLoopProps {
  params: Promise<{
    integrationId: string;
  }>;
}

// Position options


const HumanInTheLoop: React.FC<HumanInTheLoopProps> = ({ params }) => {
  const { integrationId } = React.use(params);

  return (
    <CopilotKit
      runtimeUrl={`/api/copilotkit/${integrationId}`}
      showDevConsole={false}
      agent="human_in_the_loop"
    >
      <TransferPortalAssistant />
    </CopilotKit>
  );
};

interface Step {
  description: string;
  status: "disabled" | "enabled" | "executing";
}

const InterruptHumanInTheLoop: React.FC<{
  event: { value: { steps: Step[] } };
  resolve: (value: string) => void;
}> = ({ event, resolve }) => {
  let initialSteps: Step[] = [];
  if (event.value && event.value.steps && Array.isArray(event.value.steps)) {
    initialSteps = event.value.steps.map((step: any) => ({
      description: typeof step === "string" ? step : step.description || "",
      status: typeof step === "object" && step.status ? step.status : "enabled",
    }));
  }

  const [localSteps, setLocalSteps] = useState<Step[]>(initialSteps);

  const handleCheckboxChange = (index: number) => {
    setLocalSteps((prevSteps) =>
      prevSteps.map((step, i) =>
        i === index
          ? {
            ...step,
            status: step.status === "enabled" ? "disabled" : "enabled",
          }
          : step,
      ),
    );
  };

  return (
    <div className="flex flex-col gap-4 w-[500px] bg-gray-100 rounded-lg p-8 mb-4">
      <div className="text-black space-y-2">
        <h2 className="text-lg font-bold mb-4">Select Steps</h2>
        {localSteps.map((step, index) => (
          <div key={index} className="text-sm flex items-center">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={step.status === "enabled"}
                onChange={() => handleCheckboxChange(index)}
                className="mr-2"
              />
              <span className={step.status !== "enabled" ? "line-through" : ""}>
                {step.description}
              </span>
            </label>
          </div>
        ))}
        <button
          className="mt-4 bg-gradient-to-r from-purple-400 to-purple-600 text-white py-2 px-4 rounded cursor-pointer w-48 font-bold"
          onClick={() => {
            const selectedSteps = localSteps
              .filter((step) => step.status === "enabled")
              .map((step) => step.description);
            resolve("The user selected the following steps: " + selectedSteps.join(", "));
          }}
        >
          ✨ Perform Steps
        </button>
      </div>
    </div>
  );
};

const TransferPortalAssistant = () => {
  // const [filters, setFilters] = useState({
  //   positionGap: "PF",
  //   styleOfPlay: "Transition offense",
  //   developmentReadiness: "Multi-year potential",
  //   minutesPerGame: 23,
  //   efficiencyRating: 55,
  //   reboundBlockAssist: 54,
  //   availability: {
  //     stillAvailable: true,
  //     committed: false,
  //     draftBound: false
  //   }
  // });
  const initialFilters: FilterState = {
    filters: {
      positionGap: "PF",
      // styleOfPlay: "Transition offense",
      // developmentReadiness: "Multi-year potential",
      // minutesPerGame: 22,
      efficiencyRating: 54,
      team: "",
      class_ : "JR"

      // reboundBlockAssist: 55,
      // availability: {
      //   stillAvailable: true,
      //   committed: false,
      //   draftBound: false
      // }
    }
  };
  const { state: filters, setState: setFilters } = useCoAgent<FilterState>(
    {
      name: "human_in_the_loop",
      initialState: initialFilters
    }
  );

  useLangGraphInterrupt({
    render: ({ event, resolve }) => <InterruptHumanInTheLoop event={event} resolve={resolve} />,
  });
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  useCopilotAction({
    name: "filter_transfer_portal_players",
    parameters: [
      {
        name: "positionGap",
        type: "string",
      },
      // {
      //   name: "styleOfPlay",
      //   type: "string",
      // },
      // {
      //   name: "developmentReadiness",
      //   type: "string",
      // },
      // {
      //   name: "minutesPerGame",
      //   type: "number",
      // },
      {
        name: "efficiencyRating",
        type: "number",
      },
      // {
      //   name: "reboundBlockAssist",
      //   type: "number",
      // },
      // {
      //   name: "stillAvailable",
      //   type: "boolean",
      // },
      // {
      //   name: "committed",
      //   type: "boolean",
      // },
      // {
      //   name: "draftBound",
      //   type: "boolean",
      // },
      // API-based filters (new)
    {
      name: "team",
      type: "string",
      description: "Filter by specific team name (e.g., 'Montana State', 'Duke')",
    },
    {
      name: "class_",
      type: "string",
      description: "Filter by class level",
      enum: ["FR", "SO", "JR", "SR"],
    },
    
    ],
    render: ({ args, result, status }) => {
      return <StepsFeedback args={args} result={result} status={status} selectedPlayer={selectedPlayer} setSelectedPlayer={setSelectedPlayer} />;
    },
  });

  const handleFilterChange = (filterType: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleAvailabilityChange = (key: string, checked: boolean) => {
    setFilters(prev => ({
      ...prev,
      availability: {
        ...prev.availability,
        [key]: checked
      }
    }));
  };
  const handleCloseDetails = () => {
    setSelectedPlayer(null);
  };
  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Sidebar - Filters */}
      <div className="w-80 bg-white border-r border-gray-200 p-4 overflow-y-auto">
        <div className="space-y-6">
          {/* Team Filter */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Team</h3>
            <select
              className="w-full p-2 border border-gray-300 rounded-md text-sm"
              value={filters.filters.team || ''}
              onChange={(e) => handleFilterChange('team', e.target.value)}
            >
              <option value="">All Teams</option>
              {TEAM_OPTIONS.map((team) => (
                <option key={team} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </div>

          {/* Class Filter */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Class</h3>
            <select
              className="w-full p-2 border border-gray-300 rounded-md text-sm"
              value={filters.filters.class_ || ''}
              onChange={(e) => handleFilterChange('class_', e.target.value)}
            >
              <option value="">All Classes</option>
              <option value="FR">Freshman (FR)</option>
              <option value="SO">Sophomore (SO)</option>
              <option value="JR">Junior (JR)</option>
              <option value="SR">Senior (SR)</option>
            </select>
          </div>

          {/* Team Needs Focus */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Team Needs Focus</h3>
            <select
              className="w-full p-2 border border-gray-300 rounded-md text-sm"
              value={filters.filters.positionGap}
              onChange={(e) => handleFilterChange('positionGap', e.target.value)}
            >
              <option value="PG">PG</option>
              <option value="SG">SG</option>
              <option value="SF">SF</option>
              <option value="PF">PF</option>
              <option value="C">C</option>
            </select>
          </div> 

          {/* Efficiency rating slider */}
            <div className="mb-4">
              <label className="text-xs text-gray-600 mb-2 block">Efficiency rating</label>
              <input
                type="range"
                min="0"
                max="100"
                value={filters.filters.efficiencyRating}
                onChange={(e) => handleFilterChange('efficiencyRating', [0, parseInt(e.target.value)])}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0</span>
                <span>{filters.filters.efficiencyRating}</span>
                <span>100</span>
              </div>
            </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-semibold text-gray-900">Transfer Portal Assistant</h1>
            <button className="p-2 border border-gray-300 rounded-md hover:bg-gray-50">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex">
          <div className="flex-1 p-4">
            <CopilotChat
              className="h-full rounded-lg border border-gray-200"
              labels={{
                initial: "Ask about a transfer prospect",
              }}
            />
          </div>

          {/* Player Details Sidebar */}

          {selectedPlayer && (
            <div className="w-96">
              <PlayerDetails
                player={selectedPlayer}
                onClose={handleCloseDetails}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};



const PlayerCard = ({ player, onPlayerClick }) => {
  return (
    <div 
      className="bg-white rounded-lg shadow-md border border-gray-200 p-4 cursor-pointer hover:shadow-lg transition-shadow duration-200"
      onClick={() => onPlayerClick(player)}
    >
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-gray-900 truncate">
          {player.name || 'Unknown Player'}
        </h3>
        
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span className="font-medium">{player.class_ || 'N/A'}</span>
          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
            {player.position || 'N/A'}
          </span>
        </div>
        
        <div className="text-sm text-gray-500 truncate">
          {player.team || 'N/A'}
        </div>
      </div>
    </div>
  );
};

const PlayerDetails = ({ player, onClose }) => {
  // Helper function to safely get numeric values and handle 'nan' strings
  const getNumericValue = (value, defaultValue = 0) => {
    if (value === 'nan' || value === null || value === undefined) {
      return defaultValue;
    }
    const numValue = parseFloat(value);
    return isNaN(numValue) ? defaultValue : numValue;
  };

  // Helper function to format BPR values with proper colors
  const formatBPR = (value) => {
    const numValue = getNumericValue(value);
    const formatted = numValue.toFixed(2);
    if (numValue > 0) {
      return { value: `+${formatted}`, color: 'text-green-600' };
    } else if (numValue < 0) {
      return { value: formatted, color: 'text-red-600' };
    }
    return { value: formatted, color: 'text-gray-600' };
  };

  // Helper function to get height in feet and inches
  const formatHeight = (heightInInches) => {
    const inches = getNumericValue(heightInInches);
    if (inches === 0) return 'N/A';
    const feet = Math.floor(inches / 12);
    const remainingInches = inches % 12;
    return `${feet}'${remainingInches}"`;
  };

  // Helper function to get availability status color
  const getAvailabilityColor = (eligible) => {
    if (eligible === 'True' || eligible === true) {
      return 'bg-green-100 text-green-800';
    }
    return 'bg-red-100 text-red-800';
  };

  // Helper function to get availability status text
  const getAvailabilityText = (eligible, newTeam) => {
    if (eligible === 'True' || eligible === true) {
      return newTeam && newTeam !== 'nan' && newTeam !== 'N/A' ? 'Committed' : 'Available';
    }
    return 'Not Available';
  };

  const bprPredicted = formatBPR(player.bpr_predicted);
  const obprPredicted = formatBPR(player.obpr_predicted);
  const dbprPredicted = formatBPR(player.dbpr_predicted);

  return (
    <div className="w-96 bg-white border-l border-gray-200 h-full overflow-y-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 sticky top-0 z-10">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h3 className="text-xl font-bold mb-1">{player.name || 'Unknown Player'}</h3>
            <p className="text-blue-100 text-sm">
              {player.position || 'N/A'} • {player.team || 'N/A'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="ml-2 p-1 hover:bg-white hover:bg-opacity-20 rounded"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="mt-2 text-right">
          <div className="text-sm text-blue-100">Rank</div>
          <div className="text-lg font-bold">#{player.Rank || 'N/A'}</div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-6">
        {/* Basic Info */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-lg font-bold text-gray-800">
              {formatHeight(player.height)}
            </div>
            <div className="text-sm text-gray-600">Height</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-gray-800">
              {player.weight && player.weight !== 'nan' ? `${player.weight} lbs` : 'N/A'}
            </div>
            <div className="text-sm text-gray-600">Weight</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-gray-800">
              {player.class_ || 'N/A'}
            </div>
            <div className="text-sm text-gray-600">Class</div>
          </div>
        </div>

        {/* BPR Performance Metrics */}
        <div>
          <h4 className="font-semibold text-gray-800 mb-3">Performance Metrics</h4>
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-gray-50 p-3 rounded text-center">
              <div className={`text-lg font-semibold ${bprPredicted.color}`}>
                {bprPredicted.value}
              </div>
              <div className="text-xs text-gray-600">BPR</div>
            </div>
            <div className="bg-gray-50 p-3 rounded text-center">
              <div className={`text-lg font-semibold ${obprPredicted.color}`}>
                {obprPredicted.value}
              </div>
              <div className="text-xs text-gray-600">OBPR</div>
            </div>
            <div className="bg-gray-50 p-3 rounded text-center">
              <div className={`text-lg font-semibold ${dbprPredicted.color}`}>
                {dbprPredicted.value}
              </div>
              <div className="text-xs text-gray-600">DBPR</div>
            </div>
          </div>
        </div>

        {/* Team Performance */}
        <div>
          <h4 className="font-semibold text-gray-800 mb-3">Team Performance</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-blue-50 p-3 rounded">
              <div className="text-sm font-medium text-blue-800">Off Efficiency</div>
              <div className="text-xl font-bold text-blue-600">
                {getNumericValue(player.adj_team_off_eff).toFixed(1)}
              </div>
            </div>
            <div className="bg-red-50 p-3 rounded">
              <div className="text-sm font-medium text-red-800">Def Efficiency</div>
              <div className="text-xl font-bold text-red-600">
                {getNumericValue(player.adj_team_def_eff).toFixed(1)}
              </div>
            </div>
          </div>
        </div>

        {/* Additional Stats */}
        <div>
          <h4 className="font-semibold text-gray-800 mb-3">Statistics</h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-sm text-gray-600">Possessions</span>
              <span className="font-medium">{player.possessions || 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-sm text-gray-600">Plus/Minus</span>
              <span className={`font-medium ${getNumericValue(player.plus_minus) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {getNumericValue(player.plus_minus) >= 0 ? '+' : ''}{getNumericValue(player.plus_minus).toFixed(1)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-sm text-gray-600">Role</span>
              <span className="font-medium">{getNumericValue(player.role).toFixed(1)}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-100">
              <span className="text-sm text-gray-600">Team Margin</span>
              <span className={`font-medium ${getNumericValue(player.adj_team_eff_margin) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {getNumericValue(player.adj_team_eff_margin) >= 0 ? '+' : ''}{getNumericValue(player.adj_team_eff_margin).toFixed(1)}
              </span>
            </div>
          </div>
        </div>

        {/* Transfer Status */}
        <div>
          <h4 className="font-semibold text-gray-800 mb-3">Transfer Status</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Status</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getAvailabilityColor(player.eligible)}`}>
                {getAvailabilityText(player.eligible, player.new_team)}
              </span>
            </div>
            
            {player.new_team && player.new_team !== 'nan' && player.new_team !== 'N/A' && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">New Team</span>
                <span className="font-medium text-green-600">{player.new_team}</span>
              </div>
            )}
          </div>
        </div>

        {/* NIL Value */}
        {player.dollar_value_string && player.dollar_value_string !== 'nan' && (
          <div>
            <h4 className="font-semibold text-gray-800 mb-3">NIL Value</h4>
            <div className="bg-green-50 p-3 rounded text-center">
              <div className="text-xl font-bold text-green-600">{player.dollar_value_string}</div>
            </div>
          </div>
        )}

        {/* Notes */}
        {player.notes && player.notes !== 'nan' && (
          <div>
            <h4 className="font-semibold text-gray-800 mb-3">Notes</h4>
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-sm text-gray-700">{player.notes}</p>
            </div>
          </div>
        )}

        {/* Recent Updates */}
        {player.recent && player.recent !== '' && (
          <div>
            <h4 className="font-semibold text-gray-800 mb-3">Recent Updates</h4>
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                {player.recent}
              </span>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-2 pt-4 border-t border-gray-200">
          <button className="w-full py-3 px-4 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 transition-colors">
            Compare to URI roster
          </button>
          <button className="w-full py-3 px-4 bg-orange-500 text-white rounded-md font-medium hover:bg-orange-600 transition-colors">
            Flag for recruiting
          </button>
          <button className="w-full py-3 px-4 border border-gray-300 text-gray-700 rounded-md font-medium hover:bg-gray-50 transition-colors">
            View HS video
          </button>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-gray-100">
          <div className="flex justify-between items-center text-xs text-gray-500">
            <span>ID: {player.players || 'N/A'}</span>
            <span>Updated: {new Date().toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const StepsFeedback = ({ args, result, status, selectedPlayer, setSelectedPlayer }) => {
  const [accepted, setAccepted] = useState(null);

  const players = result?.result || [];
  console.log('players===>', players);
  // const [selectedPlayer, setSelectedPlayer] = useState(null);
  const handlePlayerClick = (player) => {
    console.log('selected player', player)
    setSelectedPlayer(player);
  };

  const handleCloseDetails = () => {
    setSelectedPlayer(null);
  };
  // Handle case where players is undefined or not an array
  if (!players || !Array.isArray(players)) {
    return (
      <div className="flex flex-col gap-4 w-full max-w-6xl bg-gray-100 rounded-lg p-8 mb-4">
        <div className="text-black space-y-2">
          <h2 className="text-lg font-bold mb-4">Player Results</h2>
          <div className="text-center py-8">
            <p className="text-gray-600">No player data available</p>
          </div>
        </div>
      </div>
    );
  }

  // Handle case where players array is empty
  if (players.length === 0) {
    return (
      <div className="flex flex-col gap-4 w-full max-w-6xl bg-gray-100 rounded-lg p-8 mb-4">
        <div className="text-black space-y-2">
          <h2 className="text-lg font-bold mb-4">Player Results</h2>
          <div className="text-center py-8">
            <p className="text-gray-600">No players found</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 w-full max-w-6xl bg-gray-100 rounded-lg p-8 mb-4">
      <div className="text-black space-y-2">
        <h2 className="text-lg font-bold mb-4">Player Results</h2>
        {/* Table View */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Player
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Class
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Position
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Team
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {players.map((player, index) => (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => handlePlayerClick(player)}
                        className="text-blue-600 hover:text-blue-800 font-medium text-left"
                      >
                        {player.name || 'Unknown Player'}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {player.class_ || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        {player.position || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {player.team || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      #{player.Rank || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        player.eligible === 'True' || player.eligible === true
                          ? (player.new_team && player.new_team !== 'nan' && player.new_team !== 'N/A' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-yellow-100 text-yellow-800')
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {player.eligible === 'True' || player.eligible === true
                          ? (player.new_team && player.new_team !== 'nan' && player.new_team !== 'N/A' 
                              ? 'Committed' 
                              : 'Available')
                          : 'Not Available'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        {/* Player Cards Grid */}
        {/* <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {players.map((player, index) => (
            <PlayerCard key={index} player={player}  onPlayerClick={handlePlayerClick} />
          ))}
        </div> */}

        {/* Raw Data (collapsed by default) */}
        <details className="mt-6">
          <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
            Show Raw Data
          </summary>
          <pre className="text-sm mt-2 bg-gray-50 p-4 rounded overflow-x-auto">
            {JSON.stringify(players, null, 2)}
          </pre>
        </details>
      </div>

      {accepted !== null && (
        <div className="flex justify-end">
          <div className="mt-4 bg-gray-200 text-black py-2 px-4 rounded inline-block">
            {accepted ? "✓ Accepted" : "✗ Rejected"}
          </div>
        </div>
      )}
    </div>
  );
};


export default HumanInTheLoop;