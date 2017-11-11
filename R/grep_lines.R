grep_lines <- function(expr, lines)
{
  lines[grepl(expr, lines)]
}
