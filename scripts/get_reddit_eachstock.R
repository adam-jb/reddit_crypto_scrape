
# Code to loop through 300 cryptocurrencies and search WallStreetBets for comments containing their codes
# Filters for posts in last 2 days
# Performs seniment analysis for each currency, saving the results as a row in a dataframe 
# Script outputs a dataframe with 1 row for each currency 

library(RedditExtractoR)
library(syuzhet)
library(tidyverse)
library(data.table)
library(R.utils)


args <- commandArgs(trailingOnly=TRUE)
page_thresh <- args[1]
df <- fread(args[2])
cryptos <- df$symbol
cryptos <- cryptos[nchar(cryptos) > 2]
cryptos <- cryptos[1:300]         # select 300 cryptos to search for

nrowlog = 0

for (i in 1:length(cryptos)) {
  
  #possible_get_reddit <- possibly(get_reddit, otherwise = NA)
  print(i)
  
  possibly_get_reddit <- possibly(get_reddit, otherwise = NULL)
  
  urls <- possibly_get_reddit(search_terms = cryptos[i], subreddit = "wallstreetbets", cn_threshold = 5, 
                              sort_by = "new", wait_time = 5,
                              page_threshold = page_thresh)
  

  print(i)
  #print(urls)
  
  if (!is_null(urls)[1]) {
    print('not null')
   # print(urls$comm_date)
    urls <- urls %>%
      mutate(comm_date = lubridate::dmy(comm_date)) 
    
    input_date_since <- Sys.Date() - 8       # all since last week
    urls <- urls %>% filter(comm_date >= input_date_since)
    #print(urls)
    
    if (!nrow(urls) %in% c(0, nrowlog)) {
      print('over 0 and not null')
    
      nrowlog <- nrow(urls)
      print(nrow(urls))
    
      # take all unique comments and titles, weighting titles by num_comments
      comments <- data.frame(comment = urls$comment, num_comments = rep(1, length(urls$comment)))
      comments <- bind_rows(comments, urls[, c('comment', 'num_comments')])
      comments$comment <- stringr::str_replace_all(comments$comment, "\\W+", " ")
      
      print('a')
    
      com <- comments$comment
      sent <- com %>% get_sentiment()
      detailed_sent <- com %>% get_nrc_sentiment() 
      
      print('b')
      #print(detailed_sent)
      
      df_detail_sents <- data.matrix(detailed_sent) 
      print('ba')
      
      df_detail_sents <- df_detail_sents %>% 
        matrixStats::colWeightedMeans(comments$num_comments) 
      
      print('bb')
      df_detail_sents <- df_detail_sents %>%
        matrix(nrow = 1) %>%
        as.data.frame()
      
      print('bc')
      colnames(df_detail_sents) <- colnames(detailed_sent)
      
      print('c')
      
      
      new_df <- data.frame(symbol = cryptos[i], 
                           me = mean(sent), 
                           s = sd(sent),
                           size = nrowlog,
                           wme = weighted.mean(sent, comments$num_comments))
      
      print('d')
      new_df <- cbind(new_df, df_detail_sents)
      
      print('e')
      
      if (exists('output_df')) {
        output_df = bind_rows(output_df, new_df)
      } 
      else {
        output_df = new_df
      }
      
      print(paste('exporting to', args[3]))
      fwrite(output_df, args[3])
    
    }
    
  }

}









