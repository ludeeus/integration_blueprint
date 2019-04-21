workflow "Trigger: Push" {
  on = "push"
  resolves = ["Black Code Formatter"]
}

action "Black Code Formatter" {
  uses = "lgeiger/black-action@master"
  args = "$GITHUB_WORKSPACE --check --diff"
}
