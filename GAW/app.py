from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import os

app = Flask(__name__)

# Load data
try:
    data = pd.read_csv("Synthetic_Gas_Sensor_Garbage_Dataset.csv")
    print("✓ Dataset Loaded Successfully")
    print(f"✓ Total records: {len(data)}")
    print(f"✓ Columns: {list(data.columns)}")
except Exception as e:
    print(f"✗ Error loading dataset: {e}")
    data = None

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    graph_html = None
    error_message = None

    if request.method == "POST":
        try:
            # Get form data
            methane = float(request.form.get("methane", 0))
            co2 = float(request.form.get("co2", 0))
            nh3 = float(request.form.get("nh3", 0))
            h2s = float(request.form.get("h2s", 0))

            print(f"\n📊 Processing: Methane={methane}, CO2={co2}, NH3={nh3}, H2S={h2s}")

            tolerance = 50

            # Filter data
            matched_data = data[
                (abs(data['Methane_ppm'] - methane) <= tolerance) &
                (abs(data['CO2_ppm'] - co2) <= tolerance) &
                (abs(data['NH3_ppm'] - nh3) <= tolerance) &
                (abs(data['H2S_ppm'] - h2s) <= tolerance)
            ]

            print(f"✓ Found {len(matched_data)} matching records")

            if not matched_data.empty:
                garbage_status = str(matched_data.iloc[0]['Garbage_Present'])
                risk = str(matched_data.iloc[0]['Risk_Level'])
                
                result = {
                    "garbage": garbage_status,
                    "risk": risk
                }

                # Create graph
                try:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        y=matched_data['Methane_ppm'].values.tolist(), 
                        mode='lines', 
                        name='Methane',
                        line=dict(color='#ffc107', width=2)
                    ))
                    fig.add_trace(go.Scatter(
                        y=matched_data['CO2_ppm'].values.tolist(), 
                        mode='lines', 
                        name='CO2',
                        line=dict(color='#ff6b6b', width=2)
                    ))
                    fig.add_trace(go.Scatter(
                        y=matched_data['NH3_ppm'].values.tolist(), 
                        mode='lines', 
                        name='NH3',
                        line=dict(color='#51cf66', width=2)
                    ))
                    fig.add_trace(go.Scatter(
                        y=matched_data['H2S_ppm'].values.tolist(), 
                        mode='lines', 
                        name='H2S',
                        line=dict(color='#748ffc', width=2)
                    ))

                    fig.update_layout(
                        title="Matched Gas Sensor Data",
                        template="plotly_dark",
                        height=400,
                        hovermode='x unified'
                    )

                    graph_html = pio.to_html(fig, full_html=False, config={'responsive': True})
                    print("✓ Graph generated successfully")
                except Exception as graph_error:
                    print(f"⚠ Graph generation failed: {graph_error}")
                    graph_html = None
            else:
                result = {
                    "garbage": "Not Found",
                    "risk": "N/A"
                }
                print("⚠ No matching data found within tolerance")
                
        except ValueError as ve:
            error_message = f"Please enter valid numbers for all fields. Error: {str(ve)}"
            print(f"✗ Value Error: {error_message}")
        except KeyError as ke:
            error_message = f"Missing form field: {str(ke)}"
            print(f"✗ Key Error: {error_message}")
        except Exception as e:
            error_message = f"Error processing data: {str(e)}"
            print(f"✗ Unexpected Error: {error_message}")
            import traceback
            traceback.print_exc()

    return render_template("index.html", result=result, graph=graph_html, error=error_message)


@app.route("/test", methods=["GET"])
def test():
    return jsonify({"status": "Server is running", "data_loaded": data is not None, "records": len(data) if data is not None else 0})


if __name__ == "__main__":
    print("\n Starting Urban Garbage Detection System...\n")
    app.run(debug=True, host='127.0.0.1', port=5000)