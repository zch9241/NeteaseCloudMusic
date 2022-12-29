import argparse
def main(num):
    print('Hello world.\n' * num)
 
if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('number', type=int, help='A number')
    args = parse.parse_args()
 
    main(args.number)