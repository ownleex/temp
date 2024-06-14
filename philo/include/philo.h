/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   philo.h                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ayarmaya <ayarmaya@student.42nice.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/06/11 17:42:52 by ayarmaya          #+#    #+#             */
/*   Updated: 2024/06/11 20:36:08 by ayarmaya         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PHILO_H
# define PHILO_H

# include <unistd.h>
# include <stdio.h>
# include <stdlib.h>
# include <pthread.h>
# include <sys/time.h>

typedef struct s_philosopher
{
	int					id;
	pthread_t			thread;
	pthread_mutex_t		*left_fork;
	pthread_mutex_t		*right_fork;
	long				last_meal_time;
	int					meals_eaten;
	struct s_table		*table;
}					t_philosopher;

typedef struct s_table
{
	int					num_of_philo;
	int					time_to_die;
	int					time_to_eat;
	int					time_to_sleep;
	int					num_of_meals;
	t_philosopher		*philos;
	pthread_mutex_t		print_mutex;
	pthread_mutex_t		meal_check_mutex;
	long				start_time;
	pthread_mutex_t		*mutex_fork;
}					t_table;

long	ft_atol(const char *str);
int		error(char *str);
int		init_table(t_table *table, int argc, char **argv);
int		create_threads(t_table *table);
long	get_current_time(void);
long	get_timestamp(long start_time);

#endif