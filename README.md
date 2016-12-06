# check-websites-status-from-sources

This script takes in a list of HTTP or HTTPS URLs and tries to connect 
to each one, gathering the HTTP status code (e.g., 200 or 404) from each
one.  This is put into a TSV results file.  If there was an error (e.g.,
a timeout) connecting to the URL an error message is put in the TSV in 
place of a status code.  
 
This is not just done from the point of view of a single machine.  A
list of source machines is also provided on the command line and the URL
testing is done for each of those.  This allows you to test access from
multiple points in your network.

The results file starts with a header row consisting of "url" and one
column for each source machine.  There will be a row for each of the
URLs provided with the status code (or error) for each source machine in
the corresponding column.
 
If the results file already exists, the new results will be appended to
it.

If you have the URLs in urls.txt, the source machines in sources.txt, 
and you want the results to go in status-check-result.tsv, then you 
would run the script as:

~~~~
    check-websites-status-from-sources.py sources.txt urls.txt status-check-result.tsv
~~~~

If you only want to check the access from the local machine you can take
advantage of bash's process substitution and run the script as:

~~~~
    check-websites-status-from-sources.py <(echo 127.0.0.1) urls.txt status-check-result.tsv
~~~~
