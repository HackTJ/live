# HackTJ Live

## Deployment

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Heroku

#### Deploying

1.  Click the "Deploy to Heroku" button above
2.  Set an app name
3.  Update the environment variables in the "Config vars" section
4.  Click the "Deploy app" button

#### Updating a Live Instance

1.  make your change
2.  `git commit`
3.  `git push heroku`
    -   if you see `'heroku' does not appear to be a git repository` then run `heroku git:remote -a app-name` where `app-name` is the app name you provided above.
