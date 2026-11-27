library(data.table)
library(patchwork)
library(grid)
library(ggtext)
library(tidyverse)
library(ggplot2)

# Step 1 : Generate Evaluation Metrics ----
## Input and Output ----
folder_path <- "../test/"
out_path    <- "../test/evaluation/"
dir_5f <- file.path(out_path, "5features")
dir_3f <- file.path(out_path, "3features")

dir.create(dir_5f, showWarnings = FALSE, recursive = TRUE)
dir.create(dir_3f, showWarnings = FALSE, recursive = TRUE)

## Function of Pre-aggregate each CSV file once per 'test' group ----
preaggregate_folder <- function(folder_path, feature_cols, agg_fn = mean) {
  file_list <- list.files(path = folder_path, pattern = "\\.csv$", full.names = TRUE)
  if (length(file_list) == 0L) {
    stop("No CSV files found in: ", folder_path)
  }
  
  agg_list <- vector("list", length(file_list))
  
  for (i in seq_along(file_list)) {
    f <- file_list[i]
    tryCatch({
      dt <- fread(f, showProgress = FALSE)
      present_cols <- intersect(feature_cols, names(dt))
      if (length(present_cols) == 0L) {
        stop("None of the requested feature columns found.")
      }
      
      dt[, label_logical := as.logical(label)]
      
      # Aggregate requested features per 'test' once
      agg_dt <- dt[, c(
        list(label = label_logical[1L]),
        lapply(.SD, function(x) agg_fn(x, na.rm = TRUE))
      ), by = test, .SDcols = present_cols]
      
      agg_dt[, source_file := basename(f)]
      agg_list[[i]] <- agg_dt
    }, error = function(e) {
      warning("Skipping file ", basename(f), " due to error: ", e$message)
    })
  }
  
  rbindlist(agg_list, use.names = TRUE, fill = TRUE)
}

## Function of Evaluation all thresholds from pre-aggregated data ----
evaluate_thresholds <- function(agg_dt, feature_col, agg_label, thresholds) {
  scores <- agg_dt[[feature_col]]
  labels <- agg_dt$label
  
  # Keep only rows with non-missing score and label
  valid <- !is.na(scores) & !is.na(labels)
  scores <- scores[valid]
  labels <- labels[valid]
  is_pos <- labels
  is_neg <- !labels
  
  out <- vector("list", length(thresholds))
  
  for (idx in seq_along(thresholds)) {
    th <- thresholds[idx]
    rec <- scores >= (th - 1e-12)
    rem <- !rec
    
    tp <- sum(rec & is_pos)
    fp <- sum(rec & is_neg)
    fn <- sum(rem & is_pos)
    tn <- sum(rem & is_neg)
    
    precision <- if ((tp + fp) > 0L) tp / (tp + fp) else 1
    recall    <- if ((tp + fn) > 0L) tp / (tp + fn) else 0
    f1_score  <- if ((precision + recall) > 0) 2 * (precision * recall) / (precision + recall) else 0
    
    out[[idx]] <- data.table(
      feature_col = feature_col,
      agg_fn      = agg_label,
      threshold   = th,
      TP          = tp,
      FP          = fp,
      FN          = fn,
      TN          = tn,
      Recall      = recall,
      Precision   = precision,
      F1_Score    = f1_score
    )
  }
  
  rbindlist(out)
}

## Run evaluation and export ----
feature_columns <- c(
  "5f_min_scores", "5f_max_scores", "5f_avg_scores",
  "3f_min_scores", "3f_max_scores", "3f_avg_scores"
)

thresholds <- seq(0, 1, by = 0.05)

agg_map <- list(
  min  = min,
  max  = max,
  mean = mean
)

# Pre-aggregate all features once per aggregation function
pre_agg_by_fn <- lapply(agg_map, function(fn) {
  preaggregate_folder(folder_path, feature_columns, agg_fn = fn)
})

# Helper to run all (feature_col x agg_label) pairs for one feature prefix ("5f" or "3f")
run_feature_group <- function(prefix, target_dir) {
  group_cols <- feature_columns[startsWith(feature_columns, prefix)]
  idx <- 1L
  
  for (agg_name in names(agg_map)) {
    for (f_col in group_cols) {
      agg_dt <- pre_agg_by_fn[[agg_name]]
      results_dt <- evaluate_thresholds(
        agg_dt      = agg_dt,
        feature_col = f_col,
        agg_label   = agg_name,
        thresholds  = thresholds
      )
      
      file_name <- paste0(idx, "_", f_col, "_", agg_name, ".csv")
      fwrite(results_dt, file.path(target_dir, file_name))
      idx <- idx + 1L
    }
  }
}

## Export Evaluated Metrics
run_feature_group("5f", dir_5f)
run_feature_group("3f", dir_3f)



# Step 2: Plot Performance Curve ----

# Input Dir
analysis_result_dir_5f <- "../test/evaluation/5features/" 
analysis_result_dir_3f <- "../test/evaluation/3features/" 

# Output Dir
final_vector_pdf_path_5f <- "../test/evaluation/5features/5f_performance_vectorVersion.pdf"
final_vector_pdf_path_3f <- "../test/evaluation/3features/3f_performance_vectorVersion.pdf"

# Define Colors & Legend Order
METRIC_COLORS <- c(
  "F1_Score"  = "#008000",
  "Recall"    = "#0000FF",
  "Precision" = "#FF0000"
)

METRIC_LABELS <- c(
  "F1_Score"  = expression(bolditalic("F") * bold("1")),
  "Recall"    = expression(bold("Recall")),
  "Precision" = expression(bold("Precision"))
)

## Funciton of Lightweight Text Grob Helper (Uniform 13pt typography) ----
make_label_grob <- function(label, rot = 0, fontsize = 16, fontface = "bold") {
  wrap_elements(
    full = textGrob(
      label = label,
      rot = rot,
      gp = gpar(fontsize = fontsize, fontface = fontface, fontfamily = "sans")
    )
  )
}

## Function of Single Subplot Generator ----
create_performance_plot <- function(file_path, plot_index, col_title = NULL, sub_text = NULL) {
  
  df <- read_csv(
    file_path,
    na = c("", "NA", "NaN", "nan", "NULL", "null", "None", "Inf", "-Inf"),
    show_col_types = FALSE
  ) %>%
    mutate(across(c(threshold, Recall, Precision, F1_Score), as.numeric))
  
  show_x <- plot_index %in% 7:9
  show_y <- plot_index %in% c(1, 4, 7)
  
  df_long <- df %>%
    pivot_longer(
      cols = names(METRIC_COLORS),
      names_to = "Metric",
      values_to = "Value"
    ) %>%
    mutate(Metric = factor(Metric, levels = names(METRIC_COLORS)))
  
  ggplot(df_long, aes(x = threshold, y = Value, color = Metric)) +
    geom_line(linewidth = 1) +
    scale_color_manual(values = METRIC_COLORS) +
    labs(
      title    = col_title,
      subtitle = sub_text,
      x        = "",
      y        = ""
    ) +
    scale_y_continuous(
      limits = c(0, 1),
      breaks = seq(0, 1, 0.2),
      minor_breaks = seq(0, 1, 0.1),
      labels = function(x) sprintf("%.1f", x),
      expand = expansion(mult = c(0.01, 0.02))
    ) +
    scale_x_continuous(
      limits = c(0, 1),
      breaks = seq(0, 1, 0.2),
      minor_breaks = seq(0, 1, 0.1),
      labels = function(x) sprintf("%.1f", x),
      expand = expansion(mult = c(0.01, 0.02))
    ) +
    theme_minimal(base_size = 13) +
    theme(
      plot.title = if (!is.null(col_title)) {
        element_text(hjust = 0.5, size = 16, face = "bold", margin = margin(b = 4))
      } else {
        element_blank()
      },
      plot.subtitle = if (!is.null(sub_text)) {
        element_markdown(hjust = 0.5, size = 11, face = "plain", color = "grey15", margin = margin(b = 5), lineheight = 1.2)
      } else {
        element_blank()
      },
      panel.grid.major = element_line(color = "grey65", linewidth = 0.45),
      panel.grid.minor = element_line(color = "grey85", linewidth = 0.25),
      axis.line = element_line(color = "grey30", linewidth = 0.45),
      axis.ticks = element_line(color = "grey30", linewidth = 0.45),
      axis.ticks.length = unit(3, "pt"),
      axis.title.x = element_blank(),
      axis.title.y = element_blank(),
      axis.text.x = if (show_x) {
        element_text(size = 9, color = "black", margin = margin(t = 3))
      } else {
        element_blank()
      },
      axis.text.y = if (show_y) {
        element_text(size = 9, color = "black", margin = margin(r = 3))
      } else {
        element_blank()
      },
      legend.position = "none",
      plot.margin = margin(t = 6, r = 8, b = 4, l = 8, unit = "pt")
    )
}

## Function of Main 3x3 Grid Assembler ----
generate_performance_plot_grid <- function(folder_path, subplot_labels = NULL) {
  
  csv_files <- sort(list.files(path = folder_path, pattern = "\\.csv$", full.names = TRUE))
  
  if (length(csv_files) != 9) {
    stop(sprintf("Found %d files. Expected 9 CSV files for a 3x3 grid.", length(csv_files)))
  }
  
  if (!is.null(subplot_labels) && length(subplot_labels) != 9) {
    stop(sprintf("Provided %d subplot labels. Expected exactly 9 labels (one per subplot).", length(subplot_labels)))
  }
  
  headers <- c("Min", "Max", "Average")
  
  # Build all 9 subplots (Order: Row 1 [1-3], Row 2 [4-6], Row 3 [7-9])
  plots <- imap(csv_files, function(file, idx) {
    col_title <- if (idx <= 3) headers[idx] else NULL
    sub_text  <- if (!is.null(subplot_labels)) subplot_labels[idx] else NULL
    create_performance_plot(file, idx, col_title = col_title, sub_text = sub_text)
  })
  
  # Build standalone horizontal bottom legend
  legend_df <- expand_grid(
    Metric = factor(names(METRIC_COLORS), levels = names(METRIC_COLORS)),
    x = c(1, 2)
  ) %>%
    mutate(y = 1)
  
  legend_plot <- ggplot(legend_df, aes(x = x, y = y, color = Metric)) +
    geom_line(linewidth = 2.5) +
    scale_color_manual(values = METRIC_COLORS, labels = METRIC_LABELS) +
    theme_void() +
    theme(
      legend.position = "bottom",
      legend.direction = "horizontal",
      legend.title = element_blank(),
      legend.key.width = unit(24, "pt"),
      legend.text = element_text(
        size = 16,
        face = "bold",
        margin = margin(l = 5, r = 18)
      )
    )
  
  # Extract the non-empty guide-box (compatible with ggplot2 >= 3.5.0 and older)
  g <- ggplotGrob(legend_plot)
  guide_grobs <- g$grobs[grep("^guide-box", g$layout$name)]
  valid_guide <- Filter(function(x) !inherits(x, "zeroGrob"), guide_grobs)[[1]]
  common_legend <- wrap_elements(full = valid_guide)
  
  # Create unified 13pt labels
  global_left_label <- make_label_grob("Aggregation Function on Dataset Similarities", rot = 90, fontsize = 20, fontface = "bold")
  row_labels        <- map(headers, ~ make_label_grob(.x, rot = 90, fontsize = 16, fontface = "bold"))
  right_score_label <- make_label_grob("Similarity Score", rot = -90, fontsize = 20, fontface = "bold")
  global_x_label    <- make_label_grob("Similarity Threshold", rot = 0, fontsize = 20, fontface = "bold")
  
  # Assemble 3 rows
  rows <- map(1:3, function(r) {
    idx <- ((r - 1) * 3 + 1):(r * 3)
    (row_labels[[r]] | plots[[idx[1]]] | plots[[idx[2]]] | plots[[idx[3]]]) +
      plot_layout(widths = c(0.05, 1, 1, 1))
  })
  
  # Single centered "Similarity Score" label on the right
  grid_body <- (global_left_label | (rows[[1]] / rows[[2]] / rows[[3]]) | right_score_label) +
    plot_layout(widths = c(0.04, 1, 0.04))
  
  # Stack X-axis label ("Similarity Threshold") first, then Legend directly underneath
  aligned_x_label <- (plot_spacer() | global_x_label | plot_spacer()) + plot_layout(widths = c(0.04, 1, 0.04))
  aligned_legend  <- (plot_spacer() | common_legend  | plot_spacer()) + plot_layout(widths = c(0.04, 1, 0.04))
  
  final_plot <- (grid_body / aligned_x_label / aligned_legend) +
    plot_layout(heights = c(10, 0.45, 0.65)) +
    plot_annotation(
      title = "Aggregation Function on Data Field Similarities",
      theme = theme(
        plot.title = element_text(size = 20, face = "bold", hjust = 0.5, margin = margin(b = 10))
      )
    )
  
  return(final_plot)
}

## Produce the Plots ----

save_performance_plot <- function(folder_path, subplot_labels, filename,
                                  width = 15, height = 10, units = "in",
                                  device = cairo_pdf) {
  img <- generate_performance_plot_grid(
    folder_path    = folder_path,
    subplot_labels = subplot_labels
  )
  
  ggsave(
    filename = filename,
    plot     = img,
    device   = device,
    width    = width,
    height   = height,
    units    = units
  )
  
  invisible(filename)
}

my_subplot_texts_3f <- c(
  "<i>\u03B1</i> = 0; <i>F</i>1<sub><i>max</i></sub> = 0.23; <i>R</i> = 1; <i>P</i> = 0.13",       # 1: Min / Min
  "<i>\u03B1</i> = 0.55; <i>F</i>1<sub><i>max</i></sub> = 0.29; <i>R</i> = 0.55; <i>P</i> = 0.20", # 2: Min / Max
  "<i>\u03B1</i> = 0.2; <i>F</i>1<sub><i>max</i></sub> = 0.29; <i>R</i> = 0.61; <i>P</i> = 0.19",  # 3: Min / Average
  "<i>\u03B1</i> = 0.25; <i>F</i>1<sub><i>max</i></sub> = 0.41; <i>R</i> = 0.56; <i>P</i> = 0.32", # 4: Max / Min
  "<i>\u03B1</i> = 1; <i>F</i>1<sub><i>max</i></sub> = 0.24; <i>R</i> = 0.99; <i>P</i> = 0.14",    # 5: Max / Max
  "<i>\u03B1</i> = 0.75; <i>F</i>1<sub><i>max</i></sub> = 0.41; <i>R</i> = 0.51; <i>P</i> = 0.35", # 6: Max / Average
  "<i>\u03B1</i> = 0.1; <i>F</i>1<sub><i>max</i></sub> = 0.38; <i>R</i> = 0.47; <i>P</i> = 0.32",  # 7: Average / Min
  "<i>\u03B1</i> = 0.9; <i>F</i>1<sub><i>max</i></sub> = 0.31; <i>R</i> = 0.66; <i>P</i> = 0.20",  # 8: Average / Max
  "<i>\u03B1</i> = 0.5; <i>F</i>1<sub><i>max</i></sub> = 0.34; <i>R</i> = 0.56; <i>P</i> = 0.24"   # 9: Average / Average
)

my_subplot_texts_5f <- c(
  "<i>\u03B1</i> = 0; <i>F</i>1<sub><i>max</i></sub> = 0.23; <i>R</i> = 1; <i>P</i> = 0.13",       # 1: Min / Min
  "<i>\u03B1</i> = 0.55; <i>F</i>1<sub><i>max</i></sub> = 0.29; <i>R</i> = 0.55; <i>P</i> = 0.20", # 2: Min / Max
  "<i>\u03B1</i> = 0.15; <i>F</i>1<sub><i>max</i></sub> = 0.30; <i>R</i> = 0.57; <i>P</i> = 0.20", # 3: Min / Average
  "<i>\u03B1</i> = 0.15; <i>F</i>1<sub><i>max</i></sub> = 0.41; <i>R</i> = 0.45; <i>P</i> = 0.37", # 4: Max / Min
  "<i>\u03B1</i> = 1; <i>F</i>1<sub><i>max</i></sub> = 0.24; <i>R</i> = 0.99; <i>P</i> = 0.14",    # 5: Max / Max
  "<i>\u03B1</i> = 0.5; <i>F</i>1<sub><i>max</i></sub> = 0.43; <i>R</i> = 0.71; <i>P</i> = 0.31",  # 6: Max / Average
  "<i>\u03B1</i> = 0.05; <i>F</i>1<sub><i>max</i></sub> = 0.37; <i>R</i> = 0.35; <i>P</i> = 0.39", # 7: Average / Min
  "<i>\u03B1</i> = 0.9; <i>F</i>1<sub><i>max</i></sub> = 0.31; <i>R</i> = 0.67; <i>P</i> = 0.20",  # 8: Average / Max
  "<i>\u03B1</i> = 0.4; <i>F</i>1<sub><i>max</i></sub> = 0.40; <i>R</i> = 0.41; <i>P</i> = 0.38"   # 9: Average / Average
)


save_performance_plot(
  folder_path    = analysis_result_dir_3f,
  subplot_labels = my_subplot_texts_3f,
  filename       = final_vector_pdf_path_3f
)

save_performance_plot(
  folder_path    = analysis_result_dir_5f,
  subplot_labels = my_subplot_texts_5f,
  filename       = final_vector_pdf_path_5f
)





