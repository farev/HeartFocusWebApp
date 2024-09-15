import logging
import flask
from flask import request, jsonify, render_template
from terra.base_client import Terra

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger("app")

terra = Terra(api_key="gFbEGLBB-289H3TqDSwlMN1MsZlwIBbf", dev_id="4actk-heartfocus-testing-zC3CEBBRcu", secret="5eccbf99273d0bbc9b655ce5ba7898dceb166fd0c0213d46")

app = flask.Flask(__name__)

heart_rate_summary = {}  # Global variable to store heart rate data

@app.route("/consumeTerraWebhook", methods=["POST"])
def consume_terra_webhook() -> flask.Response:
    body = request.get_json()

    #_LOGGER.info("Received webhook for user %s of type %s", body.get("user", {}).get("user_id"), body["type"])
    
    verified = terra.check_terra_signature(request.get_data().decode("utf-8"), request.headers['terra-signature'])

    global heart_rate_summary

    if verified:
        # Extract heart rate data
        if body.get("data"):
            heart_rate_data = body.get("data")[0]["heart_rate_data"]
        else:
            heart_rate_data = None
        #print(heart_rate_data)

        if heart_rate_data:
            # Extract summary heart rate information
            summary = heart_rate_data.get("summary", {})
            avg_hr_bpm = summary.get("avg_hr_bpm")
            max_hr_bpm = summary.get("max_hr_bpm")
            min_hr_bpm = summary.get("min_hr_bpm")
            resting_hr_bpm = summary.get("resting_hr_bpm")
            
            # Extract detailed heart rate samples if needed
            detailed = heart_rate_data.get("detailed", {})
            hr_samples = detailed.get("hr_samples", [])
            
            # Log or process the extracted heart rate data
            _LOGGER.info(f"Average HR: {avg_hr_bpm}, Max HR: {max_hr_bpm}, Min HR: {min_hr_bpm}, Resting HR: {resting_hr_bpm}")
            _LOGGER.info(f"HR Samples: {hr_samples}")
            
            # Return a response with the extracted heart rate data
            heart_rate_summary = {
                    "avg_hr_bpm": avg_hr_bpm,
                    "max_hr_bpm": max_hr_bpm,
                    "min_hr_bpm": min_hr_bpm,
                    "resting_hr_bpm": resting_hr_bpm,
                    "hr_samples": hr_samples
            }

            return jsonify(heart_rate_summary), 200
    
        else:
            _LOGGER.warning("No heart rate data found")
            return flask.Response(status=404)
        
        #return flask.Response(status=200)
    else:
      return flask.Response(status=403)
    
    
@app.route("/showHeartRate")
def show_heart_rate():
    global heart_rate_summary
    return render_template("heart_focus.html", data=heart_rate_summary)

    
    
if __name__ == "__main__":
    app.run(host="localhost", port=8080)