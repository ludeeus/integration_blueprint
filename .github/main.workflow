workflow "Trigger: Push to master from admin account" {
  on = "push"
  resolves = [
    "HA Index",
    "push"
  ]
}

workflow "Trigger: Push" {
  on = "push"
  resolves = [
    "Black Code Formatter Check"
  ]
}


action "branch-filter" {
  uses = "actions/bin/filter@master"
  args = "branch master"
}

action "Access control" {
  uses = "ludeeus/actions/accesscontrol@master"
  env = {
    ACTION_LEVEL = "admin"
  }
  secrets = ["GITHUB_TOKEN"]
}

action "HA Index" {
  uses = "ludeeus/actions/haindex@master"
  secrets = ["GITHUB_TOKEN"]
  needs = ["branch-filter", "Access control"]
}

action "Black Code Formatter Fix" {
  uses = "lgeiger/black-action@v1.0.1"
  args = "$GITHUB_WORKSPACE"
}

action "Black Code Formatter Check" {
  uses = "lgeiger/black-action@v1.0.1"
  args = "$GITHUB_WORKSPACE --check"
}

action "push" {
  uses = "ludeeus/actions/push@master"
  env = {
    PUSHMAIL = "ludeeus@gmail.com"
    PUSHNAME = "ludeeus"
    PUSHBRANCH = "master"
    PUSHMESSAGE = "Action commit"
  }
  needs = ["Black Code Formatter Fix"]
  secrets = ["GITHUB_TOKEN"]
}