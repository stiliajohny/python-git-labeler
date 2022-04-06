#!/bin/env python3

import argparse
import shutil
import logging
import sys
import re
from pyfiglet import Figlet
import yaml
import requests


# A function that checks if a binary is installed on the system
def check_binary(binary):
    """ Check if a binary is installed on the system

    Args:
        binary (string): The binary to check

    Returns:
        bool: True if the binary is installed, False otherwise
    """
    logging.debug('Checking if \'' + binary + '\' is installed')
    try:
        # check if the binary is installed
        if shutil.which(binary):
            logging.debug('Binary \'' + binary + '\' is installed')
            return True
        else:
            logging.error('Binary \'' + binary + '\' is not installed')
            return False
    except Exception as e:
        logging.error(e)
        sys.exit()


# A function for the argument parser
# add the arguments repo, file, action, verbosing
def arg_parser():
    """Create the argument parser

    Returns:
        object: An object containing the arguments
    """

    parser = argparse.ArgumentParser(description='Change labels to multiple repos in one go', epilog='Use it with care :B')
    parser.add_argument('--config', help='This file contains repos and files to be copied', required=True)
    parser.add_argument('-v', '--verbose', help='Increase output verbosity', action='store_true')
    parser.add_argument('--token', help='Github API token', required=False)
    # parser.add_argument('--create-example', help='Create an example config file', action='store_true')
    args = parser.parse_args()
    return args

# Banner
def banner(text):
    """Print a banner

    Args:
        text (string): The text to print
    """
    try:
        # create a figlet object
        f = Figlet(font='slant')
        # print the banner
        print(f.renderText(text))
    except Exception as e:
        logging.error(e)
        sys.exit()

# Check the if argument verboose is set and return DEBUG or INFO
def check_verbose(args):
    """Check if the verbose argument is set

    Args:
        args (_type_): _description_

    Returns:
        _type_: _description_
    """
    if args.verbose:
        return logging.DEBUG
    else:
        return logging.INFO

# write a method that reads a yaml file and returns a dictionary
def read_yaml(file):
    """Read a yaml file and return a dictionary

    Args:
        file (_type_): _description_

    Returns:
        _type_: _description_
    """
    # read the yaml file
    with open(file, 'r') as stream:
        try:
            # load the yaml file
            logging.debug('Yaml file: ' + file + ' loaded')
            data = yaml.safe_load(stream)
            logging.debug("Yaml data: " + str(data))
            # return the dictionary
            return data
        except yaml.YAMLError as exc:
            logging.error(exc)
            sys.exit()

# A functons that opens a file and return its context
def repo_list(repos):
    """ Create a list of repositories from a file or a string

    Args:
        repos (string): file containing a list of repositories or a single repository url
    Returns:
        dict: A dictionary containing the repositories
    """
    try:
        logging.debug('Creating a list of repositories')
        # check if path is string
        if isinstance(repos, str):
            # check if the file exists
            if re.match("^(([A-Za-z0-9]+@|http(|s)\:\/\/)|(http(|s)\:\/\/[A-Za-z0-9]+@))([A-Za-z0-9.]+(:\d+)?)(?::|\/)([\d\/\w.-]+?)(\.git){1}$", repos):
                logging.debug('Using regex pattern')
                logging.debug('Repository: ' + repos)
                return repos
            # if is not a file or a url exit
            else:
                logging.error('The file or url provided is not valid')
                sys.exit()
        else:
            logging.error('The input is not a string or not input provided')
            sys.exit()
    except Exception as e:
        if e == 'No such file or directory':
            logging.error('File does not exist: ' + repos)
        elif e == 'Not a valid URL':
            logging.error('Not a valid URL: ' + repos)
            sys.exit()
        else:
            logging.error(e)
            sys.exit()

# function that creates an example config file
def create_config_example():
    """Create an example config file

    Returns:
        _type_: _description_
    """
    try:
        print('Creating an example config file')
        config = """
repos:
  - name: test1
    url: git@github.com:stiliajohny/test1.git
  - name: test2
    url: git@github.com:stiliajohny/test2.git

github_api_url: https://api.github.com

labels:
  - name: example1
    description: This is a description
    color: ff0000
    state: present
  - name: example2
    description: This is a description
    color: ff0000
    state: present
  - name: example3
    description: This is a description
    color: ff0000
    state: absent
        """
        # write this dictionary to a file
        with open('example_config.yaml', 'w') as outfile:
            yaml.dump(yaml.safe_load(config), outfile, default_flow_style=False)
            print('Example config file created at ./example_config.yaml')
        sys.exit()

    except Exception as e:
        logging.error(e)
        sys.exit()

# create a fundtion that uses the github api to read labels from a repo
def read_labels(api_url= None,owner=None, repo=None , api_token=None):
    """Read labels from a repo

    Args:
        owner (_type_, optional): _description_. Defaults to None.
        repo (_type_, optional): _description_. Defaults to None.
        api_token (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    try:
        logging.debug('Reading labels from repo: ' + repo + ' owned by: ' + owner)
        # call the github api to read labels from a repo
        url = api_url + 'repos/' + owner + '/'+ repo + '/labels'
        headers = {'Authorization': 'token %s' % api_token}
        # add an Accept header as well
        headers={'Accept': 'application/vnd.github.v3+json'}
        # make a GET request to the github api
        r = requests.get(url, headers=headers)
        logging.debug('Response: ' + str(r.status_code))
        logging.debug("labels from repo: " + repo + " owned by: " + owner + ": " + str(r.json()))
        return r.json()
    except Exception as e:
        logging.error(e)
        sys.exit()

# create a function that uses the github api to create a label
def update_label(api_url= None, owner=None, repo=None, name=None, color=None, description=None, api_token=None):
    """Write a label to a repo

    Args:
        owner (_type_, optional): _description_. Defaults to None.
        repo (_type_, optional): _description_. Defaults to None.
        name (_type_, optional): _description_. Defaults to None.
        color (_type_, optional): _description_. Defaults to None.
        api_token (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    try:
        url = api_url + 'repos/' + owner + '/'+ repo + '/labels/' + name
        logging.debug('URL: ' + url)
        headers = {'Authorization': 'token %s' % api_token, 'Accept': 'application/vnd.github.v3+json'}
        payload = '{"name": "' + name.title() + '", "color": "' + color + '", "description": "' + description + '"}'
        # make a patch request and send the data payload
        r = requests.patch(url, headers=headers, data=payload)
        logging.info('Update label: ' + name + ' to repo: ' + repo + ' owned by: ' + owner)
        logging.debug('Response: ' + str(r.status_code) + ", " + str(r.text))
        # if the response is 200 return the status code and the repsponse
        # if the response is not 200 throw an exception
        if r.status_code == 200:
            return r.status_code, r.text
        elif r.status_code != 200:
            logging.error('Error: ' + str(r.status_code) + ", " + str(r.text))
            sys.exit()
        return r.status_code
    except Exception as e:
        logging.error(e)
        sys.exit()

#  creae a function that uses the github api to create a label
def create_label(api_url=None, owner=None, repo=None, name=None, color=None, description=None, api_token=None):
    try:
        url = api_url + 'repos/' + owner + '/'+ repo + '/labels'
        # url = 'https://api.github.com/repos/' + owner + '/'+ repo + '/labels'
        logging.info('URL: ' + url)
        headers = {'Authorization': 'token %s' % api_token, 'Accept': 'application/vnd.github.v3+json'}
        payload = '{"name": "' + name.title() + '", "color": "' + color + '", "description": "' + description + '"}'
        # make a post request and send the data payload
        r = requests.post(url, headers=headers, data=payload)
        logging.info('Create label: ' + name + ' to repo: ' + repo + ' owned by: ' + owner)
        logging.debug('Response: ' + str(r.status_code) + ", " + str(r.text))
        # if the response is 200 return the status code and the repsponse
        # if the response is not 200 throw an exception
        if r.status_code == 201:
            return r.status_code, r.text
        elif r.status_code != 201:
            logging.error('Error: ' + str(r.status_code) + ", " + str(r.text))
            sys.exit()
        return r.status_code
    except Exception as e:
        logging.error(e)
        sys.exit()

# A function that uses the github api to delete a label
def delete_label(api_url=None, owner=None, repo=None, name=None, api_token=None):
    try:
        url = api_url + 'repos/' + owner + '/'+ repo + '/labels/' + name
        logging.debug('URL: ' + url)
        headers = {'Authorization': 'token %s' % api_token, 'Accept': 'application/vnd.github.v3+json'}
        # make a delete request and send the data payload
        r = requests.delete(url, headers=headers, )
        logging.info('Delete label: ' + name + ' to repo: ' + repo + ' owned by: ' + owner)
        logging.debug('Response: ' + str(r.status_code) + ", " + str(r.text))
        # if the response is 200 return the status code and the repsponse
        # if the response is not 200 throw an exception
        if r.status_code == 204:
            return r.status_code, r.text
        elif r.status_code != 204:
            logging.error('Error: ' + str(r.status_code) + ", " + str(r.text))
            sys.exit()
        return r.status_code
    except Exception as e:
        logging.error(e)
        sys.exit()

# A function that uses the github api to check if a label exists
def check_label(api_url=None, owner=None, repo=None, name=None, api_token=None):
    try:
        url = api_url + 'repos/' + owner + '/'+ repo + '/labels/' + name
        logging.debug('URL: ' + url)
        headers = {'Authorization': 'token %s' % api_token, 'Accept': 'application/vnd.github.v3+json'}
        r = requests.patch(url, headers=headers)
        if r.status_code == 200:
            logging.debug('Label: ' + name + ' already exists in repo: ' + repo + ' owned by: ' + owner)
            return True
        elif r.status_code != 200:
            logging.info('Label: ' + name + ' doesnt exists in repo: ' + repo + '. Response: ' + str(r.status_code))
        return False
    except Exception as e:
        logging.error(e)
        sys.exit()

# create a function that checks the label description length
def check_desc_length(description=None):
    if len(description) > 100:
        logging.error('Label description length is: '+ str(len(description)) +  '. Max length is 100 characters.')
        sys.exit()
    else:
        logging.debug('Label description is less than 100 characters')
        return description

def main():
    """Main function"""
    banner("Github Labeler")

    args = arg_parser()
    token = args.token
    log_format = '%(asctime)s - %(levelname)5s - %(filename)20s:%(lineno)5s - %(funcName)20s()  - %(message)s'
    logging.basicConfig(level=check_verbose(args), format=log_format)
    logging.debug('Arguments: ' + str(args))
    check_binary('git')

    config = read_yaml(args.config)
    github_api_url = config['github_api_url']
    if github_api_url[-1] != '/':
        github_api_url = github_api_url + '/'
    logging.debug('Github API URL: ' + github_api_url)

    for repo in config['repos']:
        repo = str(repo['url'])
        repo = str(repo.strip('\n'))
        logging.debug('Repo: ' + repo)
        repo_name = repo.rsplit('/', maxsplit=1)[-1].split('.')[0]
        owner_name = repo.split(':')[1].split('/')[0]
        # json_labels = read_labels(github_api_url, owner_name, repo_name, token)

        for config_label in config['labels']:
            logging.debug('Checking if label: ' + config_label['name'] + ' exists')
            label_exists = check_label(github_api_url, owner_name, repo_name, config_label['name'], token)

            # check the sugested state of a label
            if config_label['state'] == 'present':
                # if the label exists then update the label
                check_desc_length(config_label['description'])
                if label_exists:
                    update_label(github_api_url, owner_name, repo_name, config_label['name'], config_label['color'],config_label['description'], token)
                elif not label_exists:
                    create_label(github_api_url, owner_name, repo_name, config_label['name'], config_label['color'], config_label['description'], token)
            elif config_label['state'] == 'absent' and label_exists:
                logging.info('Delete label: ' + config_label['name'])
                delete_label(github_api_url, owner_name, repo_name, config_label['name'], token)


if __name__ == '__main__':
    main()
