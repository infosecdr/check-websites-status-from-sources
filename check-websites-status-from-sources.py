#!/usr/bin/env python

import csv
from argparse import ArgumentParser
from pipes import quote
from fabric.context_managers import hide
from fabric.exceptions import NetworkError
from fabric.operations import run
from fabric.state import env
import subprocess

# TODO: switch to using fabric's execute() to run multiple things in parallel (http://docs.fabfile.org/en/1.10/usage/parallel.html)
# possible TODO: switch to one result per row instead of combining multiple into same row


""" use fabric to test status code from going to a given URL; returns status code or some string error """
def get_via_fabric_status_code_for_url_connection(url):
    print "get_via_fabric_status_code_for_url_connection(%s)" % (url)
    # will get NetworkError if cannot ssh to source host

    # TODO: remove -k
    cmd='curl -s -S -o /dev/null -k -w "%{{http_code}}" --globoff --connect-timeout 10 --max-time 15 {}'.format(quote(url))
    print env.host_string+": "+cmd

    # run via subprocess or fabric's run command; both ways we set stdouterr_text and return_code variables to interpret the result
    stdouterr_text = None
    return_code = None
    if env.host_string == "127.0.0.1": # run locally rather than on a remote host
        try:
            stdouterr_text = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            return_code = 0
        except subprocess.CalledProcessError, e:
            return_code = e.returncode
            stdouterr_text = e.output
    else:
        with hide('warnings'):
            output = run(cmd)
        stdouterr_text = str(output)
        return_code = output.return_code

    print ">>"+stdouterr_text+"<<"
    if return_code > 0:
        pass # for now ignoring return code

    return stdouterr_text

usage_desc = \
    'check-websites-status-from-sources.py checks each of a given list of URLs from of a given list of source hosts.' \
    '  The status code (or error message) is gathered for each combination and it is put into a TSV table as output.'
parser = ArgumentParser(description=usage_desc)
parser.add_argument('sources_file', metavar='sources-file', type=str, help='sources file (one source IP per line)')
parser.add_argument('urls_file', metavar='urls-file', type=str, help='URLs file (one URL per line')
parser.add_argument('results_file', metavar='results-file', type=str, help='the file to write/append the results to')
args = parser.parse_args()


env.warn_only = True # make errors form running remote commands non-fatal
env.use_shell = False # make it the default that remote commands we send are not run through a shell
env.timeout = 3 # how long we will wait to SSH to any given source IP

# load urls
urls = []
with open(args.urls_file, 'rb') as urlsin:
    for url_line in urlsin:
        url = url_line.rstrip().lstrip() # trim any whitespace (including the newline)
        urls.append(url)
print "will try all sources with these urls: "+str(urls)

# load sources
sources = []
with open(args.sources_file, 'r') as sourcesin:
    for source_line in sourcesin:
        source = source_line.rstrip().lstrip() # trim any whitespace (including the newline)
        sources.append(source)

print "saving results to {}".format(args.results_file)
with open(args.results_file, 'ab') as result_out_fh:
    resultout = csv.writer(result_out_fh, delimiter='\t') # write to the results file as TSV

    resultout.writerows([['url']+sources]) # first line is "url" and the sources
    for url in urls:
        row = [url]
        for source in sources:
            env.host_string = source # switch over running tests from this source
            # test_time = time.time()
            try:
                status_code_or_err = get_via_fabric_status_code_for_url_connection(url)
                print status_code_or_err
                cell = status_code_or_err
            except NetworkError as e:
                cell = str(e) # make the exception string the cell
            # print ">"+cell+"<"

            cell = cell.replace('\n','\\n').replace('\r','\\r').replace('\t','\\t')
            row.append(cell)

        # we completed all the tests for this URL
        resultout.writerows([row])
        #result_out_fh.flush()


