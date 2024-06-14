/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   init.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ayarmaya <ayarmaya@student.42nice.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/06/11 17:35:54 by ayarmaya          #+#    #+#             */
/*   Updated: 2024/06/12 18:21:11 by ayarmaya         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "philo.h"

int	init_philosophers(t_table *table)
{
	int		i;

	table->philos = malloc(sizeof(t_philosopher) * table->num_of_philo);
	if (!table->philos)
		return (error("Err: Memory allocation failed.\n"));
	i = 0;
	while (i < table->num_of_philo)
	{
		table->philos[i].id = i + 1;
		table->philos[i].left_fork = &table->mutex_fork[i];
		table->philos[i].right_fork = &table->mutex_fork[(i + 1) % \
		table->num_of_philo];
		table->philos[i].last_meal_time = table->start_time;
		table->philos[i].meals_eaten = 0;
		table->philos[i].table = table;
		i++;
	}
	return (0);
}

int	init_forks(t_table *table)
{
	int	i;

	table->mutex_fork = malloc(sizeof(pthread_mutex_t) * table->num_of_philo);
	if (!table->mutex_fork)
		return (error("Err: Memory allocation failed.\n"));
	i = 0;
	while (i < table->num_of_philo)
	{
		if (pthread_mutex_init(&table->mutex_fork[i], NULL))
			return (error("Err: Mutex initialization failed.\n"));
		i++;
	}
	return (0);
}

int	init_table(t_table *table, int argc, char **argv)
{
	table->num_of_philo = ft_atol(argv[1]);
	table->time_to_die = ft_atol(argv[2]);
	table->time_to_eat = ft_atol(argv[3]);
	table->time_to_sleep = ft_atol(argv[4]);
	if (argc == 6)
		table->num_of_meals = ft_atol(argv[5]);
	else
		table->num_of_meals = -1;
	table->start_time = get_current_time();
	if (pthread_mutex_init(&table->print_mutex, NULL))
		return (error("Err: Print mutex initialization failed.\n"));
	if (pthread_mutex_init(&table->meal_check_mutex, NULL))
		return (error("Err: Meal check mutex initialization failed.\n"));
	if (init_forks(table))
		return (1);
	if (init_philosophers(table))
		return (1);
	return (0);
}
