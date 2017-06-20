# vowel-discri
Predictive models of effect sizes in infant vowel discrimination

## Fetching from our private OSF repository

This will only work for users registered in our OSF project.

You need python 3.4+ and jasonapi-requests (obtained with `pip install jsonapi-requests` in the terminal for example).

First copy `_osf_auth_template.py` to `_osf_auth.py` and add your OSF credentials in the newly created file. Your credentials will remain private because the `.gitignore` file is configured so that your `_osf_auth.py` will never be commited to the git repository.

You can now run `python osf_fetch_example.py`.
