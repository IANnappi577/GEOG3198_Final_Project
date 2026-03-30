## Guide to Using Github with Git

### TLDR; The most important commands


#### Git Push: transfer code you wrote online. Essentially, "push" code to the repository

1. Write some code
2. Open a terminal shell in VSCodium, which opens along the bottom screen
3. type `git status`, you should see a list of <span style="color:red">red</span> files. Those are files not yet "committed" to be pushed
4. type `git add -A` --> this adds all the red files to your "stage"
5. type `git commit -m "<your message>"` where you replace `<your message>` with a short description of what you changed. Make sure to include quotes around the message. For example, `"I finished code for myfunction()"`.
6. type `git push` --> this will push your changes to the repository
7. If you want to verify that it worked, go to the <a href="https://github.com/IANnappi577/GEOG3198_Final_Project">repository URL</a> and see if your name and commit message shows up under the commits banner here:

<img src="./assets/git_push_verification.png">


#### Git Pull: update your local computer's copy of the code with any changes the other person made. Essentially, "pull" from the repository

1. Open a terminal shell in VSCodium, which opens along the bottom screen
2. type `git status`, and make sure that it says the following:

```code
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

2. ...If it doesn't say this, you still have changes in your local computer that are not on the repository. You can't do a `git pull` if any of the file icons in the left `Explorer` tab of VSCodium are either <span style="color:yellow">yellow</span> or <span style="color:green">green</span>.
3. If you passed step 2, type `git pull origin main` --> this will pull the code from the repository onto your local computer

> Important: if there are any errors that are thrown in this process, just text me the error codes. Git can get really finiky really quickly if you do something just slightly off, so I don't blame you if it's confusing.

### FAQ

#### When should I push new code I wrote?

You can push as often or as infrequently as you'd like. Our repository has no rules, unlike what I need to follow for my capstone project haha. Just _maybe_ not too many pushes per day! (like maybe no more than 3 a day, but that's not a hard rule)

--> More FAQs as they come up