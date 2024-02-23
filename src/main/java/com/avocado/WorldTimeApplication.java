package com.avocado;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class WorldTimeApplication
{
public static void main(String[] args) 
{
SpringApplication.run(WorldTimeApplication.class, args);
}
}