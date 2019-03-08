workflow "Trigger: Push to master from admin account" {
  on = "push"
  resolves = [
    "HA Index"
  ]
}

workflow "Trigger: Push" {
  on = "push"
  resolves = [
    "Black Code Formatter"
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

action "Black Code Formatter" {
  uses = "lgeiger/black-action@v1.0.1"
  args = "$GITHUB_WORKSPACE --check"
}