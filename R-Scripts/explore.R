
library(readr)
library(tidyverse)
library(lubridate)
library(gridExtra)

fork_results <- read_csv("C:/Users/Mikes_Surface2/PycharmProjects/Gov_Social_Coding_Replication/data/fork_results.csv")

repo_results = read.csv("C:\\Users\\Mikes_Surface2\\PycharmProjects\\Gov_Social_Coding_Replication\\data\\repo_results.csv")

fork_results <- fork_results %>% mutate(created_at = ymd_hms(created_at),
                                        pushed_at = ymd_hms(pushed_at),
                                        updated_at = ymd_hms(pushed_at))

##2628000 = one month in seconds
##31536000 = one year in seconds

depts_interest = c("EPA","NASA","DOC","DOE","DOJ","USDA","DOD")
fork_time <- fork_results %>% filter(created_at < ymd_hms(20210101000000)) %>% ggplot(aes(created_at)) + geom_freqpoly(binwidth = 31536000) 


repo_results <- repo_results %>% mutate(created_at = ymd_hms(created_at),
                                        pushed_at = ymd_hms(pushed_at),
                                        updated_at = ymd_hms(pushed_at))

repo_time <- repo_results %>% filter(created_at < ymd(20210101)) %>% ggplot(aes(created_at)) + geom_freqpoly(binwidth = 31536000) 

grid.arrange(fork_time,repo_time)


fork_results %>% filter(created_at < ymd_hms(20201120000000)) %>% 
                 filter(forker_dept %in% depts_interest) %>%
              ggplot(aes(created_at)) + geom_freqpoly(binwidth = 2628000) +facet_wrap(~repo_dept)



str(repo_results$department)
levels(repo_results$department)




fork_nums <- fork_results %>% group_by(forker_org) %>% summarise(count = n())
forks_from <- fork_results %>% group_by(repo_org) %>% summarise(count = n())

