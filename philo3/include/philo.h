/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   philo.h                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ayarmaya <ayarmaya@student.42nice.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/06/11 17:42:52 by ayarmaya          #+#    #+#             */
/*   Updated: 2024/06/23 16:29:26 by ayarmaya         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PHILO_H
# define PHILO_H

# include <unistd.h>
# include <stdio.h>
# include <stdlib.h>
# include <pthread.h>
# include <sys/time.h>

# define MAX_PHILO 200

typedef struct s_philo
{
	pthread_t		thread;
	int				id;
	int				eating;
	int				meals_eaten;
	size_t			last_meal;
	size_t			time_to_die;
	size_t			time_to_eat;
	size_t			time_to_sleep;
	size_t			start_time;
	int				num_of_philos;
	int				num_times_to_eat;
	int				*dead;
	pthread_mutex_t	*r_fork;
	pthread_mutex_t	*l_fork;
	pthread_mutex_t	*write_lock;
	pthread_mutex_t	*dead_lock;
	pthread_mutex_t	*meal_lock;
}					t_philo;
typedef struct s_program
{
	int				dead_flag;
	pthread_mutex_t	dead_lock;
	pthread_mutex_t	meal_lock;
	pthread_mutex_t	write_lock;
	t_philo			*philos;
}					t_program;

// utils
size_t	get_current_time(void);
int		ft_usleep(size_t milliseconds);
void	destroy_all(char *str, t_program *program, pthread_mutex_t *forks);
int		ft_atoi(char *str);
int		ft_strlen(char *str);

// main
int		check_valid_args(char **argv);
int		check_arg(char *str);
int		ft_malloc(t_philo **philos, pthread_mutex_t **forks, \
		int philo_num);

// init
void	init_program(t_program *program, t_philo *philos);
void	init_forks(pthread_mutex_t *forks, int philo_num);
void	init_philos(t_philo *philos, t_program *program, \
		pthread_mutex_t *forks, char **argv);
void	init_input(t_philo *philo, char **argv);

// threads
int		thread_create(t_program *program, pthread_mutex_t *forks);
void	*philo_routine(void *pointer);
int		dead_loop(t_philo *philo);

// routines
void	eat(t_philo *philo);
void	dream(t_philo *philo);
void	think(t_philo *philo);

// monitor
void	*monitor(void *pointer);
int		check_if_all_ate(t_philo *philos);
int		check_if_dead(t_philo *philos);
int		philosopher_dead(t_philo *philo, size_t time_to_die);
void	print_message(char *str, t_philo *philo, int id);

#endif