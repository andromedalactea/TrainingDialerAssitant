
# Import local modules
from scripts.weebhook_calification import *
from scripts.call_vapi_api import *

def main_flux():
    # Server URL
    domain = "loosely-stirred-porpoise.ngrok-free.app"  # El subdominio que reservaste
    url_server = f"https://{domain}/calificate_call"
    # Extract the number to be called from the command line execution
    number = sys.argv[1]

    # Call the AI
    call = call_ai(number, url_server) 
    if call == "Call made":
        print_to_console("Call made")
    else: 
        print_to_console("Error making the call.. Verify the number and format")
        print_to_console(r'Example format "+18065133220"')
        os.kill(os.getpid(), signal.SIGINT)

    os.kill(os.getpid(), signal.SIGINT)

    ## Start the weebhook to receive the call end data
    # Define the port of your choice, by default Flask uses port 5000
    port = 5000
    # Configure ngrok with the port on which Flask is running
    ngrok_tunnel = ngrok.connect(port, domain=domain)

    # Run the Flask server, making sure it is publicly accessible and on the correct port
    app.run(host='0.0.0.0', port=5000)

    # Disconnect the ngrok tunnel when you are ready to end the session
    ngrok.disconnect(ngrok_tunnel.public_url)

    return "Flux finished"


# Example Usage
if __name__ == '__main__':
    main_flux()