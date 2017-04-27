#!/usr/bin/env python2
import argparse
import os
import shlex
import subprocess

import yaml


def loadYmlFile(path):
    try:
        file = open(path, "r")
        try:
            return yaml.load(file)
        except yaml.YAMLError as e:
            print e.message
    except IOError as e:
        print "Error: Wrong project path or " + path + " doesn't exist"


def populate(types, php, dir, index):
    processes = []
    outputs = []

    print "Found types:"
    for t in types:
        print "  - {t}".format(t=t)
        processes.append(subprocess.Popen(shlex.split(
            '{php} {dir}/app/console fos:elastica:populate --index={index} --type={t} --no-reset'.format(php=php,
                                                                                                         dir=dir,
                                                                                                         index=index,
                                                                                                         t=t)),
            stdout=subprocess.PIPE))

    print "\nPopulating Elastica"
    while processes:
        p = processes[0]
        p.wait()
        outputs.append(p.stdout.read())
        print('\nProceess ID: {p} - finished'.format(p=p.pid))
        os.sys.stdout.flush()
        processes.remove(p)

    print "\nOutput:"
    for out in outputs:
        print out


def main():
    parser = argparse.ArgumentParser(os.path.basename(__file__),
                                     description='Populate elastica for Syfmony based application.')
    parser.add_argument('dir', help='Main directory of Symfony project')
    parser.add_argument('--php', help='Path to PHP binary. If not defined - use default php', default='php')
    parser.add_argument('--index', help='Population type. If not defined - use default from elastic.yml')
    args = parser.parse_args()

    yamlElastic = loadYmlFile(path=args.dir + "/app/config/elastic.yml")

    index = []
    for k, v in yamlElastic['fos_elastica']['indexes'].items():
        index = k

    args.index = index if args.index == None else args.index

    types = []
    for k, v in yamlElastic['fos_elastica']['indexes'][index]['types'].items():
        types.append(k)

    populate(types=types, php=args.php, dir=args.dir, index=index)


if __name__ == "__main__":
    main()
