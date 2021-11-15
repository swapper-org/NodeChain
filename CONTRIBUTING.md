# Contributing

First off, thank you for considering contributing to NodeChain. It's people like you that make NodeChain better.

When contributing to NodeChain, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Please note we have a code of conduct, please follow it in all your interactions with the project.

## Your First Contribution

If this is your first time contributing to the project, and you don't want to commit, there are other tasks you can do to be a hero:

- Review a [Pull Request](https://github.com/swapper-org/NodeChain/pulls).
- Fix an [Issue](https://github.com/swapper-org/NodeChain/issues).
- Update the [docs](https://docs.nodechain.swapper.market).
- Write a tutorial.
- Enhance the project's identity.
- Spread the project.

## Contributing to development

### Issue Process

Have you noticed any **bugs** or have any **feature** requests? You can submit any request [here](https://github.com/swapper-org/NodeChain/issues/new).

It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

### Pull Request Process

We use forking to contributing the project.

For more information, you can check this [Git guide](https://git-scm.com/book/en/v2/GitHub-Contributing-to-a-Project) about forking.

#### Fork & Create a branch

If this is something you think you can fix, improve or add, then [fork NodeChain](https://git-scm.com/book/en/v2/GitHub-Contributing-to-a-Project) and create a branch with a descriptive name.

A good branch name would be (where issue **#123** is the issue you're working on):

```sh
git checkout -b 123-support-bitcoin-cash-rpc-api
```

#### Get your project running

Before you start coding, you need to test if your project is running in your machine.
Check out the [README](https://github.com/swapper-org/NodeChain/blob/master/README.md) to warm up and set up the project.

#### Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help, everyone is a beginner at first.

#### Run lint and tests

Before submitting a pull request, make sure your changes don't break any functionality of the project. Check out the [README](https://github.com/swapper-org/NodeChain/blob/master/README.md) to see how can you do it.

#### Make a Pull Request

At this point, you should switch back to your staging branch and make sure it's up to date with NodeChain's staging branch:

```sh
git remote add upstream git@github.com:swapper-org/NodeChain.git
git checkout staging
git pull upstream staging
```

Then update your feature branch from your local copy of staging, and push it!

```sh
git checkout 123-support-bitcoin-cash-rpc-api
git rebase staging
git push --set-upstream origin 123-support-bitcoin-cash-rpc-api
```

Finally, go to GitHub and make a [Pull Request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request) 😄

#### Keeping your Pull Request updated

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

To learn more about rebasing in Git, there are a lot of good resources as [Github docs](https://docs.github.com/en/github/getting-started-with-github/about-git-rebase) or [Git-SCM docs](https://git-scm.com/book/en/v2/Git-Branching-Rebasing), but here's the suggested workflow:

```sh
git checkout 123-support-bitcoin-cash-rpc-api
git pull --rebase upstream staging
git push --force-with-lease origin 123-support-bitcoin-cash-rpc-api
```

### Merging a PR (maintainers only)

A PR can only be merged into staging by a maintainer if:

- It is passing CI.
- It has been approved by at least two maintainers. If it was a maintainer who opened the PR, only one extra approval is needed.
- It has no requested changes.
- It is up to date with current staging.

A PR can only be merged from staging into master by a maintainer if:

- It is passing CI.
- It is approved to move to the next production version by the rest of the maintainers.
- It has the documentation up to date.
- It is up to date with current master.

Any maintainer is allowed to merge a PR if all of these conditions are met.

### Releases (maintainers only)

Currently, NodeChain is using a versioning based on two digits (**vX.Y**).
Where **"X"** is **Production stage** version (master branch) and **"Y"** is **Staging/Test stage** version (staging branch).

This may change for minor changes This may change for minor changes and hotfixes, where a three-digit versioning will be used (**vX.Y.Z**).
Where **"Z"** is **Staging stage** version with the **hotfix** (staging branch)

This may change and improve in the future.

## Contributing to documentation

Our Swagger documentation is in the [NodeChain docs](https://github.com/swapper-org/NodeChain-docs) repository.
It is divided by **master branch versions**.

### Fork and create branch

If our branch **#123** in NodeChain repository is making any changes in the documentation, then [fork NodeChain docs](https://git-scm.com/book/en/v2/GitHub-Contributing-to-a-Project) and create a branch with the same name.

```sh
git checkout -b 123-support-bitcoin-cash-rpc-api
```

### Make the changes

Now you can make any necessary changes in the documentation, remember to ask for help if you need it!

### Make a Pull Request

At this point, you should switch back to your staging branch and make sure it's up to date with NodeChain-docs's staging branch:

```sh
git remote add upstream git@github.com:swapper-org/NodeChain-docs.git
git checkout staging
git pull upstream staging
```

Then update your feature branch from your local copy of staging, and push it!

```sh
git checkout 123-support-bitcoin-cash-rpc-api
git rebase staging
git push --set-upstream origin 123-support-bitcoin-cash-rpc-api
```

Finally, go to GitHub and make a [Pull Request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request) 😄

### Link your docs PR to the main PR

Once you make your Pull Request in NodeChain-docs, copy the link and add it to your Pull Request in NodeChain repository.
There is a section called "Related PR or Docs PR" to paste it!

### Keeping your Pull Request updated

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

To learn more about rebasing in Git, there are a lot of good resources as [Github docs](https://docs.github.com/en/github/getting-started-with-github/about-git-rebase) or [Git-SCM docs](https://git-scm.com/book/en/v2/Git-Branching-Rebasing), but here's the suggested workflow:

```sh
git checkout 123-support-bitcoin-cash-rpc-api
git pull --rebase upstream staging
git push --force-with-lease 123-support-bitcoin-cash-rpc-api
```

## Contributor Covenant Code of Conduct

### Our Pledge

We as members, contributors, and leaders pledge to make participation in our community a harassment-free experience for everyone, regardless of age, body size, visible or invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, caste, color, religion, or sexual identity and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming, diverse, inclusive, and healthy community.

### Our Standards

Examples of behavior that contributes to a positive environment for our community include:

- Demonstrating empathy and kindness toward other people.
- Being respectful of differing opinions, viewpoints, and experiences.
- Giving and gracefully accepting constructive feedback.
- Accepting responsibility and apologizing to those affected by our mistakes, and learning from the experience.
- Focusing on what is best not just for us as individuals, but for the overall community.

Examples of unacceptable behavior include:

- The use of sexualized language or imagery, and sexual attention or advances of any kind.
- Trolling, insulting or derogatory comments, and personal or political attacks.
- Public or private harassment.
- Publishing others' private information, such as a physical or email address, without their explicit permission.
- Other conduct which could reasonably be considered inappropriate in a professional setting.

### Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of acceptable behavior and will take appropriate and fair corrective action in response to any behavior that they deem inappropriate, threatening, offensive, or harmful.

Community leaders have the right and responsibility to remove, edit, or reject comments, commits, code, wiki edits, issues, and other contributions that are not aligned to this Code of Conduct, and will communicate reasons for moderation decisions when appropriate.

### Scope

This Code of Conduct applies within all community spaces, and also applies when an individual is officially representing the community in public spaces.
Examples of representing our community include using an official e-mail address, posting via an official social media account, or acting as an appointed representative at an online or offline event.

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the community leaders responsible for enforcement at <swapper@swapper.market>. All complaints will be reviewed and investigated promptly and fairly.

All community leaders are obligated to respect the privacy and security of the reporter of any incident.

### Enforcement Guidelines

Community leaders will follow these Community Impact Guidelines in determining the consequences for any action they deem in violation of this Code of Conduct:

#### 1. Correction

**Community Impact**: Use of inappropriate language or other behavior deemed unprofessional or unwelcome in the community.

**Consequence**: A private, written warning from community leaders, providing clarity around the nature of the violation and an explanation of why the behavior was inappropriate. A public apology may be requested.

#### 2. Warning

**Community Impact**: A violation through a single incident or series of actions.
**Consequence**: A warning with consequences for continued behavior. No interaction with the people involved, including unsolicited interaction with those enforcing the Code of Conduct, for a specified period of time. This includes avoiding interactions in community spaces as well as external channels like social media. Violating these terms may lead to a temporary or permanent ban.

#### 3. Temporary Ban

**Community Impact**: A serious violation of community standards, including sustained inappropriate behavior.

**Consequence**: A temporary ban from any sort of interaction or public communication with the community for a specified period of time. No public or private interaction with the people involved, including unsolicited interaction with those enforcing the Code of Conduct, is allowed during this period.
Violating these terms may lead to a permanent ban.

#### 4. Permanent Ban

**Community Impact**: Demonstrating a pattern of violation of community standards, including sustained inappropriate behavior, harassment of an individual, or aggression toward or disparagement of classes of individuals.

**Consequence**: A permanent ban from any sort of public interaction within the community.

### Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org/), version 2.0, available at https://www.contributor-covenant.org/version/2/0/code_of_conduct.html.

Some text is adapted from the [Contributing guidelines of Active Admin](https://github.com/activeadmin/activeadmin/blob/master/CONTRIBUTING.md). Thanks for this amazing guide!
