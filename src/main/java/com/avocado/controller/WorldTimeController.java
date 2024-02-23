package com.avocado.controller;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
public class WorldTimeController
{
    @Value("${api.url}")
    private String apiURL;

    @RequestMapping("/")
    public String worldTime()
    {
        try {
            RestTemplate restTemplate = new RestTemplate();
            String response = restTemplate.getForObject(apiURL, String.class);
            response = response.replace("\n", "<br/>");
            response = "<b>" + response + "</b>";
            return response;
        }catch (Exception e){
            return "Unable to reach " + apiURL + "<br/>" + System.currentTimeMillis();
        }
    }

    @RequestMapping("/hello")
    public String hello()
    {
        return "<h1>Hello</h1>" + "<br/><h3>" + System.currentTimeMillis() + "</h3>";
    }
}
