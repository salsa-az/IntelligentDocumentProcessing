import azure.functions as func
import json 
import logging
from analyst_chain import analyst_function_executor
from letterfunc import letter_chain_pro
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger_analyst")
def http_trigger_analyst(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    try:
        customer_id = req.params.get("customer_id")
        claim_id = req.params.get("claim_id")

        if not customer_id or not claim_id:
            return func.HttpResponse(
                "Missing required query parameters: customer_id and claim_id",
                status_code=400
            )

        # 1. Tangkap hasil eksekusi ke dalam variabel 'result'
        result = analyst_function_executor(customer_id, claim_id)
        
        # 2. Kembalikan 'result' sebagai respons JSON
        # Pastikan 'result' adalah tipe data yang bisa diubah ke JSON (seperti dict atau list)
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            "Something went wrong while processing the request.",
            status_code=500
        )
    
@app.route(route="http_trigger_notify")
def http_trigger_notify(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    try:
        customer_id = req.params.get("customer_id")
        claim_id = req.params.get("claim_id")
        approval_id = req.params.get("approval_id")

        if not customer_id or not claim_id:
            return func.HttpResponse(
                "Missing required query parameters: customer_id and claim_id",
                status_code=400
            )

        # 1. Tangkap hasil eksekusi ke dalam variabel 'result'
        result = letter_chain_pro(customer_id, claim_id, approval_id)
        # 2. Kembalikan 'result' sebagai respons JSON
        # Pastikan 'result' adalah tipe data yang bisa diubah ke JSON (seperti dict atau list)
        return func.HttpResponse(
            json.dumps(result),
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            "Something went wrong while processing the request.",
            status_code=500
        )
    
