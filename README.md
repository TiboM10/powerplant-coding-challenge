# Solution to the Engie powerplant coding challenge

## Getting the Repository

Clone the repository with:

```
git clone https://github.com/TiboM10/powerplant-coding-challenge
```

## Setting up

Enter into the cloned project:
```
cd powerplant-coding-challenge/
```
You will need `Python 3.10+` and `flask 2.0.0+` to run the project.

Flask can be installed with:
```
pip install -r requirements.txt
```

## Running the application

Run the localhost server:
```
python main.py
```

Send payloads:
```
curl -X POST -d @example_payloads/payload1.json -H "Content-Type: application/json" http://localhost:8888/productionplan
```
Where <payload1> can be any of the provided payloads in /example_payloads.

This will return the response as a printed json file of the powerplants and their delivered power.

# Solution Algorithm

The algorithm to find an optimal solution works as follows:

Compute the merit order of the powerplants as the fuel cost divided by effiency, adding co2 taxes to the cost of gas-powered plants.
Lower merit score means more preferable, wind turbines have cost 0 and thus are most desirable to use.

Compute the power for each powerplant in order of merit, taking into account the Pmin and Pmax.
If necessary, adapt the power of the previous plant to fit Pmin. A windturbine is either on or off.

Repeat the previous step until the total load is reached, then return the computed power that each plant has to deliver for this solution.
