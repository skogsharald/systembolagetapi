# -*- coding: utf-8 -*-
import argparse
from systembolagetapi_app import app


def main(args):
    if args.debug:
        print '---- RUNNING IN DEBUG MODE ----'
    app.run(debug=args.debug)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Systembolaget REST API.')
    parser.add_argument('--debug', help='Run in debug mode.', action='store_true', default=False)
    main(parser.parse_args())
