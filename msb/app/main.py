from fastapi import FastAPI
from data import meldingen
app = FastAPI()

# meldingen = meldingen()

@app.get("/api/")
async def root():
    melding_list = [m.get("list") for m in meldingen() if m.get("detail")]
    print(len(melding_list))

    return melding_list

@app.get("/api/")
async def root():
    melding_list = [m.get("list") for m in meldingen() if m.get("detail")]
    print(len(melding_list))

    return melding_list