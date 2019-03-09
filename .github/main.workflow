workflow "Trigger: Push to master from admin account" {
  on = "push"
  resolves = [
    "HA Index"
  ]
}

action "branch-filter" {
  uses = "actions/bin/filter@master"
  args = "branch master"
}

action "Access control" {
  uses = "ludeeus/action-accesscontrol@master"
  env = {
    ACTION_LEVEL = "admin"
  }
  secrets = ["GITHUB_TOKEN"]
}

action "HA Index" {
  uses = "ludeeus/action-haindex@master"
  secrets = ["GITHUB_TOKEN"]
  needs = ["branch-filter", "Access control"]
}