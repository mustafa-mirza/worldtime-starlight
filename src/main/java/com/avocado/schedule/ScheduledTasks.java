package com.avocado.schedule;

import java.text.SimpleDateFormat;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
@ConditionalOnProperty(prefix = "api.call.schedule", name="enable", havingValue="true", matchIfMissing = true)
public class ScheduledTasks {

    private static final Logger log = LoggerFactory.getLogger(ScheduledTasks.class);

    private static final SimpleDateFormat dateFormat = new SimpleDateFormat("HH:mm:ss");

    @Value("${api.url}")
    private String apiURL;

    @Scheduled(fixedRateString = "${api.call.interval}")
    public void logCurrentTime() {
        try {
            RestTemplate restTemplate = new RestTemplate();
            String response = restTemplate.getForObject(apiURL, String.class);
            response = response.replace("\n", ", ");
            log.info("World Time response : "+ response);
        }catch (Exception e){
            log.info("Unable to reach url " + apiURL + " . Current system time is " + System.currentTimeMillis());
        }
    }
}
