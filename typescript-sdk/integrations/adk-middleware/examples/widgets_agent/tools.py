import os
import json
from typing import Dict, List, Optional, Any
import time
from google.cloud import bigquery
from google.adk.tools import ToolContext
from datetime import datetime




def render_pie_chart(
    tool_context: ToolContext,
    title: str,
    labels: str,
    values: str,
    chart_type: str = "distribution"
) -> Dict[str, Any]:
    """
    Render a pie chart for construction data visualization.
    
    Args:
        title: Chart title describing what is being shown
        labels: Comma-separated string of category labels (e.g., "Model,Spec,Homebuyer" or "Window Covering,Tile,Carpet")
        values: Comma-separated string of numeric values corresponding to labels (e.g., "25,30,15" or "125000,85000,45000")
        chart_type: Type of chart - "distribution" for counts, "financial" for monetary values
    
    Returns:
        Success message indicating pie chart is ready for rendering
    """
    try:
        # Parse labels and values
        label_list = [label.strip() for label in labels.split(",")]
        value_list = [float(value.strip()) for value in values.split(",")]
        
        # Validate data
        if len(label_list) != len(value_list):
            return {
                "success": False,
                "error": "Number of labels must match number of values",
                "chart_data": None
            }
        
        if len(label_list) == 0:
            return {
                "success": False,
                "error": "At least one data point is required",
                "chart_data": None
            }
        
        # Calculate percentages
        total = sum(value_list)
        if total == 0:
            return {
                "success": False,
                "error": "Total values cannot be zero",
                "chart_data": None
            }
        
        percentages = [round((value / total) * 100, 1) for value in value_list]
        
        # Create chart data structure
        chart_data = {
            "title": title,
            "type": "pie",
            "chart_type": chart_type,
            "data": {
                "labels": label_list,
                "values": value_list,
                "percentages": percentages,
                "total": total
            },
            "metadata": {
                "categories": len(label_list),
                "largest_category": label_list[value_list.index(max(value_list))],
                "largest_value": max(value_list),
                "largest_percentage": max(percentages)
            }
        }
        tool_context.state["pie_chart_data"] = chart_data
        return {
            "success": True,
            "message": "Pie chart is rendered",
            "chart_data": chart_data
        }
        
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid numeric values provided: {str(e)}",
            "chart_data": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error rendering pie chart: {str(e)}",
            "chart_data": None
        }


def render_bar_chart(
    tool_context: ToolContext,
    title: str,
    labels: str,
    values: str,
    chart_type: str = "comparison",
    orientation: str = "vertical"
) -> Dict[str, Any]:
    """
    Render a bar chart for construction data visualization.
    
    Args:
        title: Chart title describing what is being shown
        labels: Comma-separated string of category labels (e.g., "Model,Spec,Homebuyer" or "Window Covering,Tile,Carpet")
        values: Comma-separated string of numeric values corresponding to labels (e.g., "25,30,15" or "125000,85000,45000")
        chart_type: Type of chart - "comparison" for comparing values, "financial" for monetary values, "distribution" for counts
        orientation: Chart orientation - "vertical" for vertical bars, "horizontal" for horizontal bars
    
    Returns:
        Success message indicating bar chart is ready for rendering
    """
    try:
        # Parse labels and values
        label_list = [label.strip() for label in labels.split(",")]
        value_list = [float(value.strip()) for value in values.split(",")]
        
        # Validate data
        if len(label_list) != len(value_list):
            return {
                "success": False,
                "error": "Number of labels must match number of values",
                "chart_data": None
            }
        
        if len(label_list) == 0:
            return {
                "success": False,
                "error": "At least one data point is required",
                "chart_data": None
            }
        
        # Validate orientation
        if orientation not in ["vertical", "horizontal"]:
            orientation = "vertical"
        
        # Calculate statistics
        total = sum(value_list)
        avg_value = total / len(value_list) if len(value_list) > 0 else 0
        max_value = max(value_list) if value_list else 0
        min_value = min(value_list) if value_list else 0
        
        # Create chart data structure
        chart_data = {
            "title": title,
            "type": "bar",
            "chart_type": chart_type,
            "orientation": orientation,
            "data": {
                "labels": label_list,
                "values": value_list,
                "total": total,
                "average": round(avg_value, 2)
            },
            "metadata": {
                "categories": len(label_list),
                "highest_category": label_list[value_list.index(max_value)],
                "highest_value": max_value,
                "lowest_category": label_list[value_list.index(min_value)],
                "lowest_value": min_value,
                "range": max_value - min_value
            }
        }
        
        tool_context.state["bar_chart_data"] = chart_data
        
        return {
            "success": True,
            "message": "Bar chart is rendered",
            "chart_data": chart_data
        }
        
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid numeric values provided: {str(e)}",
            "chart_data": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error rendering bar chart: {str(e)}",
            "chart_data": None
        }


def render_series_bar_chart(
    tool_context: ToolContext,
    title: str,
    labels: str,
    series_data: str,
    chart_type: str = "comparison",
    orientation: str = "vertical"
) -> Dict[str, Any]:
    """
    Render a series bar chart for construction data visualization with multiple data series.
    
    Args:
        title: Chart title describing what is being shown
        labels: Comma-separated string of category labels (e.g., "Q1,Q2,Q3,Q4")
        series_data: JSON string containing series information with format:
                    '[{"name": "Series1", "values": [10,20,30], "color": "#FF5733"}, 
                      {"name": "Series2", "values": [15,25,35], "color": "#33FF57"}]'
        chart_type: Type of chart - "comparison" for comparing values, "financial" for monetary values, "distribution" for counts
        orientation: Chart orientation - "vertical" for vertical bars, "horizontal" for horizontal bars
    
    Returns:
        Success message indicating series bar chart is ready for rendering
    """
    try:
        # Parse labels
        label_list = [label.strip() for label in labels.split(",")]
        
        # Parse series data
        try:
            series_list = json.loads(series_data)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON format for series_data: {str(e)}",
                "chart_data": None
            }
        
        # Validate series data structure
        if not isinstance(series_list, list):
            return {
                "success": False,
                "error": "series_data must be a JSON array",
                "chart_data": None
            }
        
        if len(series_list) == 0:
            return {
                "success": False,
                "error": "At least one series is required",
                "chart_data": None
            }
        
        # Validate each series and convert to proper structure
        validated_series = []
        for i, series in enumerate(series_list):
            if not isinstance(series, dict):
                return {
                    "success": False,
                    "error": f"Series {i+1} must be an object",
                    "chart_data": None
                }
            
            if 'name' not in series or 'values' not in series:
                return {
                    "success": False,
                    "error": f"Series {i+1} must have 'name' and 'values' properties",
                    "chart_data": None
                }
            
            try:
                values = [float(v) for v in series['values']]
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "error": f"Series {i+1} values must be numeric",
                    "chart_data": None
                }
            
            if len(values) != len(label_list):
                return {
                    "success": False,
                    "error": f"Series {i+1} values count must match labels count",
                    "chart_data": None
                }
            
            validated_series.append({
                "name": series['name'],
                "values": values,
                "color": series.get('color', f"#{'%06x' % (hash(series['name']) & 0xFFFFFF)}")
            })
        
        if len(label_list) == 0:
            return {
                "success": False,
                "error": "At least one label is required",
                "chart_data": None
            }
        
        # Validate orientation
        if orientation not in ["vertical", "horizontal"]:
            orientation = "vertical"
        
        # Calculate overall statistics
        all_values = []
        for series in validated_series:
            all_values.extend(series['values'])
        
        total = sum(all_values)
        avg_value = total / len(all_values) if len(all_values) > 0 else 0
        max_value = max(all_values) if all_values else 0
        min_value = min(all_values) if all_values else 0
        
        # Find highest and lowest categories and series
        highest_value = max_value
        lowest_value = min_value
        highest_category = ""
        highest_series = ""
        lowest_category = ""
        lowest_series = ""
        
        for series in validated_series:
            for i, value in enumerate(series['values']):
                if value == highest_value:
                    highest_category = label_list[i]
                    highest_series = series['name']
                if value == lowest_value:
                    lowest_category = label_list[i]
                    lowest_series = series['name']
        
        # Calculate series-specific statistics
        series_totals = {}
        series_averages = {}
        for series in validated_series:
            series_total = sum(series['values'])
            series_totals[series['name']] = series_total
            series_averages[series['name']] = round(series_total / len(series['values']), 2) if series['values'] else 0
        
        # Create chart data structure
        series_bar_chart_data = {
            "title": title,
            "type": "series_bar",
            "chart_type": chart_type,
            "orientation": orientation,
            "data": {
                "labels": label_list,
                "series": validated_series,
                "total": total,
                "average": round(avg_value, 2)
            },
            "metadata": {
                "categories": len(label_list),
                "series_count": len(validated_series),
                "highest_category": highest_category,
                "highest_value": highest_value,
                "highest_series": highest_series,
                "lowest_category": lowest_category,
                "lowest_value": lowest_value,
                "lowest_series": lowest_series,
                "range": max_value - min_value,
                "series_totals": series_totals,
                "series_averages": series_averages
            }
        }
        
        tool_context.state["series_bar_chart_data"] = series_bar_chart_data
        
        return {
            "success": True,
            "message": "Series bar chart is rendered",
            "series_bar_chart_data": series_bar_chart_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error rendering series bar chart: {str(e)}",
            "chart_data": None
        }


def render_data_matrix_grid(
    tool_context: ToolContext,
    title: str,
    headers: str,
    rows: str,
    grid_type: str = "data_table"
) -> Dict[str, Any]:
    """
    Render a data matrix grid for construction data visualization.
    
    Args:
        title: Grid title describing what data is being shown
        headers: Comma-separated string of column headers (e.g., "Customer,Product,Quantity,Price,Margin")
        rows: Pipe-separated rows with comma-separated values (e.g., "Customer A,Tile,100,5000,1200|Customer B,Wood,50,3000,800")
        grid_type: Type of grid - "data_table" for tabular data, "comparison_matrix" for comparison data, "summary_grid" for summary metrics
    
    Returns:
        Success message indicating data matrix grid is ready for rendering
    """
    try:
        # Parse headers
        header_list = [header.strip() for header in headers.split(",")]
        
        # Parse rows
        if not rows.strip():
            return {
                "success": False,
                "error": "No row data provided",
                "grid_data": None
            }
        
        row_list = []
        for row_str in rows.split("|"):
            row_str = row_str.strip()
            if row_str:
                row_data = [cell.strip() for cell in row_str.split(",")]
                if len(row_data) != len(header_list):
                    return {
                        "success": False,
                        "error": f"Row data count ({len(row_data)}) does not match header count ({len(header_list)})",
                        "grid_data": None
                    }
                row_list.append(row_data)
        
        if len(row_list) == 0:
            return {
                "success": False,
                "error": "At least one data row is required",
                "grid_data": None
            }
        
        # Validate grid_type
        valid_grid_types = ["data_table", "comparison_matrix", "summary_grid"]
        if grid_type not in valid_grid_types:
            grid_type = "data_table"
        
        # Detect numeric columns for statistics
        numeric_columns = []
        for col_idx, header in enumerate(header_list):
            try:
                # Check if all non-empty values in this column are numeric
                is_numeric = True
                for row in row_list:
                    if row[col_idx].strip() and row[col_idx].strip().lower() not in ['', 'n/a', 'null']:
                        try:
                            float(row[col_idx].replace(',', '').replace('$', ''))
                        except ValueError:
                            is_numeric = False
                            break
                if is_numeric:
                    numeric_columns.append(col_idx)
            except (IndexError, ValueError):
                continue
        
        # Calculate statistics for numeric columns
        statistics = {}
        for col_idx in numeric_columns:
            col_values = []
            for row in row_list:
                try:
                    if row[col_idx].strip() and row[col_idx].strip().lower() not in ['', 'n/a', 'null']:
                        value = float(row[col_idx].replace(',', '').replace('$', ''))
                        col_values.append(value)
                except (ValueError, IndexError):
                    continue
            
            if col_values:
                statistics[header_list[col_idx]] = {
                    "total": sum(col_values),
                    "average": round(sum(col_values) / len(col_values), 2),
                    "max": max(col_values),
                    "min": min(col_values),
                    "count": len(col_values)
                }
        
        # Create grid data structure
        grid_data = {
            "title": title,
            "type": "matrix_grid",
            "grid_type": grid_type,
            "data": {
                "headers": header_list,
                "rows": row_list,
                "row_count": len(row_list),
                "column_count": len(header_list)
            },
            "metadata": {
                "total_rows": len(row_list),
                "total_columns": len(header_list),
                "numeric_columns": [header_list[i] for i in numeric_columns],
                "statistics": statistics
            }
        }
        
        tool_context.state["matrix_grid_data"] = grid_data
        
        return {
            "success": True,
            "message": "Data matrix grid is rendered",
            "grid_data": grid_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error creating data matrix grid: {str(e)}",
            "grid_data": None
        }


def render_summary(
    tool_context: ToolContext,
    title: str,
    summary: str
) -> Dict[str, Any]:
    """
    Render a summary widget for displaying textual information.
    
    Args:
        title: Summary title describing what is being summarized
        summary: The summary text content to display
    
    Returns:
        Success message indicating summary is ready for rendering
    """
    try:
        # Validate inputs
        if not title.strip():
            return {
                "success": False,
                "error": "Title cannot be empty",
                "summary_data": None
            }
        
        if not summary.strip():
            return {
                "success": False,
                "error": "Summary cannot be empty",
                "summary_data": None
            }
        
        # Calculate summary statistics
        word_count = len(summary.split())
        char_count = len(summary)
        char_count_no_spaces = len(summary.replace(" ", ""))
        line_count = len(summary.split("\n"))
        
        # Create summary data structure
        summary_data = {
            "title": title,
            "type": "summary",
            "data": {
                "content": summary.strip(),
                "word_count": word_count,
                "character_count": char_count,
                "character_count_no_spaces": char_count_no_spaces,
                "line_count": line_count
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "content_type": "text",
                "is_multiline": line_count > 1
            }
        }
        
        tool_context.state["summary_data"] = summary_data
        
        return {
            "success": True,
            "message": "Summary is rendered",
            "summary_data": summary_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error rendering summary: {str(e)}",
            "summary_data": None
        }


# Make functions available for import
__all__ = [  'render_pie_chart', 'render_bar_chart', 'render_data_matrix_grid' , 'render_series_bar_chart', 'render_summary']