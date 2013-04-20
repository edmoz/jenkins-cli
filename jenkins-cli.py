#!/usr/bin/python 
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
 *
 * This is a Jenkins command line interface specific to the Persona, 
 * https://github.com/edmoz/browserid project. Currently just a one off
 * script with some hard coded URLS and paths
 */                                                                   
                                                                                             
import base64, json, optparse, os, urllib2, sys
import xml.etree.ElementTree as ET

try:
    USER = os.environ['JENKINS_USER']
    TOKEN = os.environ['JENKINS_TOKEN']
except:
    print 'please set env vars: JENKINS_USER, JENKINS_TOKEN'

PROJ_ROOT = "identity.browserid."
ROOT_URL = "https://ci.mozilla.org/view/Persona/job/"
ENV = ['dev', 'stage', 'prod']
CONFIG_PATH = '../config/configs.json'
configs = {}

def write_disk(dir, proj, data):
    '''Write text file to disk'''
    if not os.path.exists(dir):
        os.makedirs(dir)
    loc = os.path.join(dir, proj+'.xml')
    with open (loc, 'w') as f:
        f.write (data)
    print '::wrote file: %s ' % loc

def build_request(xml_url):	
    '''Create basic authorization request, returns request object'''
    req = urllib2.Request(xml_url)
    auth_encoded = base64.encodestring('%s:%s' % (USER, TOKEN))\
        .replace('\n', '')
    req.add_header('Authorization', 'Basic %s' % auth_encoded)
    return req
    
def post_url(xml_url, xml_data):
    '''Execute HTTP POST to url with data'''
    data = ET.tostring(xml_data, encoding='UTF-8')
    req = build_request(xml_url)
    req.add_header('Content-Type', 'application/xml')
    req.add_data(data)
    response = urllib2.urlopen(req)
    print "::POSTED TO JENKINS"

def get_configs(config_path):
    '''Get config strings defined in json file'''
    with open(config_path) as f:
        json_data = json.load(f)
    return [ x for x in json_data.keys()]

def get_url(xml_url, prt=True):
    '''Return config.xml at a given URL'''
    req = build_request(xml_url)
    try:
        response = urllib2.urlopen(req)
        data = response.read()
        if prt:
            print data
        print 'read in file: %s' % req.get_full_url()
        return data
    except:
        print 'unable to get url: %s' % req.get_full_url()

def read_file(file):
    '''Read a local xml file and print out specific xml node values'''
    print 'Reading', file
    tree =  ET.parse(file)
    root = tree.getroot()
    desc = root.find('description')
    cmd = root.find(".//command")
    cron = root.find(".//hudson.triggers.TimerTrigger/spec")
    branch = root.find(".//hudson.plugins.git.BranchSpec/name")
    print '::description:', desc.text
    if cron is not None:
        print '::cron:', cron.text
    if branch is not None:
        print '::branch:', branch.text
    print '::cmd:', cmd.text

    return tree, desc, cmd, cron, branch

def write_file(file, new_file, _desc = '', _cmd = '', _cron='', _branch=''):
    '''Write a local XML file with params provided'''
    tree, desc, cmd, cron, branch = read_file(file)
    desc.text = _desc
    if _cmd:
        cmd.text = _cmd
    if _cron:
        cron.text = _cron
    if _branch:
        branch.text = _branch
    tree.write(new_file, encoding="UTF-8", xml_declaration=True)
    print 
    print '::NEW FILE::'
    read_file(new_file)

if __name__ == "__main__":
    usage = """usage: jenkins-cli.py [options]
    There are two ways to use this:
    -in batch mode set by the --all which will
    create and read/write to a dir of prod|stage|dev.
    -in manual read/write specific file mode which uses --proj
    """
    p = optparse.OptionParser(usage)

    p.add_option('--proj', '-p', help='jenkins project name for single proj mode')
    p.add_option('--all', '-a', help='dev|stage|prod, batch process all projects in a given env')
    p.add_option('--write', '-w', action="store_true", help='write local file, accepts new file name in single proj mode')
    p.add_option('--read', '-r', help='path to local file')
    p.add_option('--get', '-g', action="store_true", help='print proj config')
    p.add_option('--post', action="store_true", help='post config.xml to jenkins web service')
    p.add_option('--desc', '-d', help='config.xml new description string')
    p.add_option('--cmd', '-c', help='config.xml new command string')
    p.add_option('--branch', '-b', help='config.xml new branch string')
    p.add_option('--cron', '-o', help='config.xml new cron string')
    options, arguments = p.parse_args()
    
    proj = options.proj
    desc = options.desc
    cmd = options.cmd
    cron = options.cron
    branch = options.branch
    
    if options.all:
        if not options.get and not options.write and not options.post:
            print 'Need to either --get, --write, or --post'
            sys.exit(0)
        if options.write and not desc and not branch and not cmd and not cron:
            print 'Nothing to change: need desc, branch, cmd or cron'
            sys.exit(0)
        for config in get_configs(CONFIG_PATH):
            config_url = os.path.join(ROOT_URL,'%s%s.%s' % \
                (PROJ_ROOT, options.all, config),'config.xml')
            data = get_url(config_url, False)
            local_path = os.path.join(options.all, config + '.xml')
            if not data:
                continue
            if options.get:
                write_disk(options.all, config, data)
            if options.write:
                write_file(local_path, local_path, desc, cmd, cron, branch)
            if options.post:
                xml_blob = read_file(local_path)[0].getroot()
                response = post_url(config_url, xml_blob)
    else:
        if proj:
            if proj[:len(PROJ_ROOT)] != PROJ_ROOT:
                proj = PROJ_ROOT + proj
            proj_file = proj + '.xml'
        xml_url = os.path.join(ROOT_URL, proj, 'config.xml')
        
        if options.get:
            get_url(xml_url)
        if options.read and not options.write:
            read_file(options.read)
        if options.read and options.write:
            #reads in a file and writes out specified file
            write_file(options.read, options.write, desc, cmd, cron, branch)
        if options.post:
            xml_blob = read_file(options.post)[0].getroot()
            response = post_url(xml_url, xml_blob)
    
