/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   actions.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ayarmaya <ayarmaya@student.42nice.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/06/11 18:15:46 by ayarmaya          #+#    #+#             */
/*   Updated: 2024/06/12 19:46:05 by ayarmaya         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "../include/philo.h"

void	print_action(t_philosopher *philo, const char *action)
{
	pthread_mutex_lock(&philo->table->print_mutex);
	printf("%ld %d %s\n", get_timestamp(philo->table->start_time), \
	philo->id, action);
	pthread_mutex_unlock(&philo->table->print_mutex);
}

void	eat(t_philosopher *philo)
{
	pthread_mutex_lock(philo->left_fork);
	print_action(philo, "has taken a fork");
	pthread_mutex_lock(philo->right_fork);
	print_action(philo, "has taken a fork");
	print_action(philo, "is eating");
	usleep(philo->table->time_to_eat * 1000);
	philo->last_meal_time = get_current_time();
	pthread_mutex_unlock(philo->left_fork);
	pthread_mutex_unlock(philo->right_fork);
	philo->meals_eaten++;
}

void	sleep_and_think(t_philosopher *philo)
{
	print_action(philo, "is sleeping");
	usleep(philo->table->time_to_sleep * 1000);
	print_action(philo, "is thinking");
}

void	*routine(void *arg)
{
	t_philosopher	*philo;

	philo = (t_philosopher *)arg;
	while (philo->meals_eaten < philo->table->num_of_meals)
	{
		eat(philo);
		if (philo->meals_eaten >= philo->table->num_of_meals)
			break ;
		sleep_and_think(philo);
	}
	return (NULL);
}

int	create_threads(t_table *table)
{
	int	i;

	i = 0;
	while (i < table->num_of_philo)
	{
		if (pthread_create(&table->philos[i].thread, NULL, routine, \
		&table->philos[i]))
			return (error("Err: Thread creation failed.\n"));
		i++;
	}
	i = 0;
	while (i < table->num_of_philo)
	{
		if (pthread_join(table->philos[i].thread, NULL))
			return (error("Err: Thread join failed.\n"));
		i++;
	}
	return (0);
}
