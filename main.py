import flask


powertypes = {"gasfired": "gas(euro/MWh)","turbojet": "kerosine(euro/MWh)","windturbine": "wind(%)"}


"""
Calculate fuel cost efficiency for each powerplant
"""
def calculate_costs(payload):
    for powerplant in payload["powerplants"]:
        match(powerplant["type"]):
            case "windturbine":
                powerplant["cost_efficiency"] = 0    
            case "turbojet":
                powerplant["cost_efficiency"] = payload["fuels"][powertypes["turbojet"]] / powerplant["efficiency"]
            case "gasfired":
                powerplant["cost_efficiency"] = (payload["fuels"][powertypes["gasfired"]] + 0.3 * payload["fuels"]["co2(euro/ton)"]) / powerplant["efficiency"]
            case _:
                print("invalid powerplant type")
    return payload


"""
Sort the powerplants based on fuel effiency (merit-order), then pmax
"""
def merit_order(powerplants):
    return powerplants.sort(key=lambda x: (x["cost_efficiency"], -x["pmax"]))


"""
Allocate a preferred load per powerplant in order to match the total load.
"""
def allocate_loads(load, payload): 
    powerplants = payload["powerplants"]
    production = []
    current_load = 0
    #loop over powerplant in order of merit
    for powerplant in powerplants:
        if(load == 0):
            current_load = 0

        #load too small            
        elif(load < powerplant["pmin"]):
            #check pmin of first powerplant, or all zero p before
            skipping = True
            for pplant in production:
                if pplant["p"] > 0:
                    skipping = False

            previous_plant = None
            if not skipping:
                for pplant in powerplants:
                    if pplant["name"] == production[-1]["name"]:
                        previous_plant = pplant

            if skipping:
                production.append({"name" : powerplant["name"], "p" : 0})
                continue
            #retroactively change the power from the previous powerplant to fit a Pmin that is too high, assume backtracking depth of max. 1             
            elif previous_plant["name"] == "windturbine": #windturbine has to be on/off
                production[-1]["p"] = 0 
                load += previous_plant["pmax"] * payload["fuels"]["wind(%)"] / 100.0
                current_load = min(load, powerplant["pmax"]) #assume no problems with pmin now
            else: 
                production[-1]["p"] -= powerplant["pmin"] - load
                load = powerplant["pmin"]
                current_load = load
        else:
            if(powerplant["type"] == "windturbine"): #windturbine has to be on/off
                current_load = powerplant["pmax"] * payload["fuels"]["wind(%)"] / 100.0
                if current_load > load:
                    current_load = 0 
            else:
                current_load = powerplant["pmax"] if load >= powerplant["pmax"] else load

        round(current_load,1)  
        load -= current_load
        production.append({"name" : powerplant["name"], "p" : current_load})    
    return production


def solve(payload):
    load = payload["load"]
    payload = calculate_costs(payload)
    powerplants = payload["powerplants"]
    merit_order(powerplants)
    production = allocate_loads(load, payload)
    return production


#Web Hosting Functionality
app = flask.Flask(__name__)


@app.route("/")
def main_page():
  return "Power production problem main page."


@app.route('/productionplan', endpoint='productionplan', methods=['POST'])
def production_plan():
    payload = flask.request.get_json()
    response = solve(payload)
    return flask.jsonify(response)


app.run(host="0.0.0.0", port=8888) #hosted on localhost, port 8888
