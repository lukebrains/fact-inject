import winrm

# Create the winrm session that will be used to add facts to a windows host.
# This is a helper function.
def create_winrm_session(host, username, password):
    try:
        # Create a winrm connection with winrm.
        rm = winrm.Session(host, auth=(username, password))
        return rm
    except winrm.FEATURE_OPERATION_TIMEOUT:
        print('Error: Could not connect to {}.'.format(host))
        exit(code=1)
    except winrm.FEATURE_READ_TIMEOUT:
        print('Error: Could not connect to {}.'.format(host))
        exit(code=1)

# Create all of the environment variables that will be used to create the powershell
# script that wil inject windows environment variables.
def create_win_facter_vars(facts):
    vars = []
    for item in facts.keys():
        vars.append('$env:{0}="{1}"'.format(item, facts[item]))
    return vars

# Generate the powershell script that will add all of the environment variables to the node.
def generate_ps_script(vars):
    script = ''
    for item in vars:
        script += '{};'.format(item)
    return script

# Add Facter facts to windows as environment variables.
def inject_win_facts(facts, host, username, password):
    vars = create_win_facter_vars(facts)
    script = generate_ps_script(vars)
    # Create the winrm session.
    rm = create_winrm_session(host, username, password)
    # Now run try to run the powershell on the remote host.
    result = rm.run_ps(script)
    if result.status_code != 0:
        print('Error: Could not add facts to Windows host {}.'.format(host))
        print(result.std_err)
        exit(code=1)
    else:
        print(result.std_out)