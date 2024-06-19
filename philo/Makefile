# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ayarmaya <ayarmaya@student.42nice.fr>      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/06/05 13:27:58 by ayarmaya          #+#    #+#              #
#    Updated: 2024/06/19 19:35:45 by ayarmaya         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME		=	philo
PATH_SRC	=	src/
SRC			=	main.c \
				utils.c \
				init.c \
				threads.c \
				monitor.c \
				routines.c

SRCS		=	$(addprefix $(PATH_SRC), $(SRC))
OBJS		=	$(SRCS:.c=.o)
CC			=	cc
CFLAGS		=	-Wall -Wextra -Werror -g
LDFLAGS		=	-lpthread
HEADERS		=	-I./include
RM			= 	rm -f

all:		$(NAME)

$(NAME): 	$(OBJS)
			$(CC) $(CFLAGS) $(OBJS) -o $(NAME) $(HEADERS) $(LDFLAGS)

%.o: 		%.c
			$(CC) $(CFLAGS) $(HEADERS) -c $< -o $@

clean:
			$(RM) $(OBJS)

fclean:		clean
			$(RM) $(NAME)

re:			fclean all

.PHONY:		all clean fclean re
