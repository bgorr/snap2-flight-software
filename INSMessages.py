import zmq
import insmessage_pb2 as ins_message

class INSMessages():
    def __init__(self):
        print("INSMessage init")

    def readINSmessage(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://10.4.1.100:5555")
        socket.subscribe("")
        socket.setsockopt(zmq.LINGER,500)
        socket.setsockopt(zmq.RCVTIMEO,500)
        try:
            address = socket.recv()
            message = socket.recv()
        except:
            return("INS messages not connected.")
        if (message is None):
            return("INS messages not connected.")

        ins = ins_message.RavenFCU_SWICD_INSmessage()
        ins.ParseFromString(message)
        print(ins.latitude)
        print(ins.longitude)
        print(ins.altitude)
        return ((ins.latitude,ins.longitude,ins.altitude))
        