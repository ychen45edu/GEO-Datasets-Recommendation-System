required_packages <- c(
  "data.table",
  "patchwork",
  "ggtext",
  "tidyverse",
  "ggtext"
)

missing_packages <- required_packages[!(required_packages %in% rownames(installed.packages()))]

if (length(missing_packages) > 0) {
  install.packages(missing_packages, repos = "https://cloud.r-project.org")
}