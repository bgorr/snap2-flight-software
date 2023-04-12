import zmq
import insmessage_pb2 as ins_message

class INSMessages():
    def __init__(self):
        print("INSMessage init")

    def readINSmessage():
        ip = "10.1.2.3"
        port = "5555"
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect ("tcp://%s:%s" % ip, port)

        address = socket.recv()
        message = socket.recv()

        ins = ins_message.RavenFCU_SWICD_INSmessage()
        ins.ParseFromString(message)

        print(ins.latitude)
        print(ins.longitude)
        print(ins.altitude)