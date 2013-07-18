jenkins-cli
===========

Python command line interface to jenkins config files. Currently lots of hard coded links for the jenkin's instance used for Persona/BrowserID.  Please feel free and offer up any changes to make this more generic.

Requirements: You must generate a token when you log into Jenkins by navigating to our user page, then click configure. The page may take up to 45 secs to load the first time. But there you will find your token.  Then set two env vars: JENKINS_USER, JENKINS_TOKEN.  Really it needs a config file to remove all the hard paths. Good luck.

    Usage: jenkins-cli.py [options]
        There are a few ways to use this:
        -in batch mode set by the --all which will create and read/write to a dir of prod|stage|dev.
        -in manual read/write specific file mode which uses --proj
        -in logs mode wich will fetch all jobs for a proj between two csv values: --logs=300,310
    

    Options:
      -h, --help            show this help message and exit
      -p PROJ, --proj=PROJ  jenkins project name for single proj mode
      -a ALL, --all=ALL     dev|stage|prod, batch process all projects in a given
                            env
      -w, --write           write local file, accepts new file name in single proj
                            mode
      -g, --get             print proj config
      --post                post config.xml to jenkins web service
      -r READ, --read=READ  path to local file
      -d DESC, --desc=DESC  config.xml new description string
      -c CMD, --cmd=CMD     config.xml new command string
      -b BRANCH, --branch=BRANCH
                            config.xml new branch string
      -o CRON, --cron=CRON  config.xml new cron string
      --logs=LOGS           requires proj option and a csv of: start_jid,last_jid



