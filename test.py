import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-host', '--host', type=str, default='0.0.0.0')
parser.add_argument('-p', '--port', type=str, default='5001')
parser.add_argument('-d', '--debug', type=int, default=0, choices=[0, 1])
parser.add_argument('-thr', '--threaded', type=int, default=1, choices=[0, 1])
args = parser.parse_args()
print(args.host)
print(args.port)
print(bool(args.threaded))

d = {'a':1, 'b':2}
print('a' in d)
print('b' in d)

