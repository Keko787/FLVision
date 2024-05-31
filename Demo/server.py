#########################################################
#    Imports / Env setup                                #
#########################################################

import flwr as fl

#########################################################
#    Initialize & Start Server                          #
#########################################################

fl.server.start_server(
    config=fl.server.ServerConfig(num_rounds=3)
)
