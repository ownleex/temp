/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: ayarmaya <ayarmaya@student.42nice.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/06/10 16:15:01 by ayarmaya          #+#    #+#             */
/*   Updated: 2024/06/22 15:53:13 by ayarmaya         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "philo.h"

int	allocate_resources(t_philo **philos, pthread_mutex_t **forks, int philo_num)
{
	*philos = (t_philo *)malloc(sizeof(t_philo) * philo_num);
	if (!*philos)
	{
		write(2, "Memory allocation error for philosophers\n", 41);
		return (1);
	}
	*forks = (pthread_mutex_t *)malloc(sizeof(pthread_mutex_t) * philo_num);
	if (!*forks)
	{
		free(*philos);
		write(2, "Memory allocation error for forks\n", 33);
		return (1);
	}
	return (0);
}

int	check_arg(char *arg)
{
	int	i;

	i = 0;
	while (arg[i] != '\0')
	{
		if (arg[i] < '0' || arg[i] > '9')
			return (1);
		i++;
	}
	return (0);
}

int	check_valid_args(char **argv)
{
	if (ft_atoi(argv[1]) > PHILO_MAX || ft_atoi(argv[1]) <= 0 || check_arg(argv[1]) == 1)
	{
		return (write(2, "Invalid philosophers number\n", 29), 1);
	}
	if (ft_atoi(argv[2]) <= 0 || check_arg(argv[2]) == 1)
	{
		write(2, "Invalid time to die\n", 21);
		return (1);
	}
	if (ft_atoi(argv[3]) <= 0 || check_arg(argv[3]) == 1)
	{
		write(2, "Invalid time to eat\n", 21);
		return (1);
	}
	if (ft_atoi(argv[4]) <= 0 || check_arg(argv[4]) == 1)
	{
		write(2, "Invalid time to sleep\n", 23);
		return (1);
	}
	if (argv[5] && (ft_atoi(argv[5]) < 0 || check_arg(argv[5]) == 1))
	{
		write(2, "Invalid number of times each philosopher must eat\n", 51);
		return (1);
	}
	return (0);
}

int	main(int argc, char **argv)
{
	t_program			program;
	t_philo				*philos;
	pthread_mutex_t		*forks;
	int					philo_num;

	if (argc != 5 && argc != 6)
		return (write(2, "Wrong argument count\n", 22), 1);
	if (check_valid_args(argv) == 1)
		return (1);
	philo_num = ft_atoi(argv[1]);
	if (allocate_resources(&philos, &forks, philo_num) != 0)
		return (1);
	init_program(&program, philos);
	init_forks(forks, philo_num);
	init_philos(philos, &program, forks, argv);
	thread_create(&program, forks);
	destroy_all(NULL, &program, forks);
	return (0);
}
