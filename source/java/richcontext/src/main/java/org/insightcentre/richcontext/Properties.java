package org.insightcentre.richcontext;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import org.apache.commons.lang3.builder.ReflectionToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.IOException;

/**
 * Created by fpena on 06/06/2017.
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class Properties {

    @JsonProperty("cross_validation_num_folds")
    private int crossValidationNumFolds;
    @JsonProperty("topn_n")
    private int topN;
    @JsonProperty("topn_num_items")
    private int topnNumItems;
    @JsonProperty("rival_relevance_threshold")
    private double relevanceThreshold;
    @JsonProperty("rival_seed")
    private long seed;
    @JsonProperty("rival_evaluation_strategy")
    private String strategy;
    @JsonProperty("topic_model_num_topics")
    private int numTopics;
    @JsonProperty("fm_num_factors")
    private int fmNumFactors;

    @JsonProperty("context_format")
    private String contextFormat;

    @JsonProperty("business_type")
    private String dataset;


    public static Properties loadProperties(String fileName) throws IOException {

        ObjectMapper mapper = new ObjectMapper(new YAMLFactory());

        Properties properties =
                    mapper.readValue(new File(fileName), Properties.class);
        System.out.println(ReflectionToStringBuilder.toString(
                properties, ToStringStyle.MULTI_LINE_STYLE));
        System.out.println(properties.toString());

        return properties;
    }

    public int getCrossValidationNumFolds() {
        return crossValidationNumFolds;
    }

    public void setCrossValidationNumFolds(int crossValidationNumFolds) {
        this.crossValidationNumFolds = crossValidationNumFolds;
    }

    public int getTopN() {
        return topN;
    }

    public void setTopN(int topN) {
        this.topN = topN;
    }

    public int getTopnNumItems() {
        return topnNumItems;
    }

    public void setTopnNumItems(int topnNumItems) {
        this.topnNumItems = topnNumItems;
    }

    public double getRelevanceThreshold() {
        return relevanceThreshold;
    }

    public void setRelevanceThreshold(double relevanceThreshold) {
        this.relevanceThreshold = relevanceThreshold;
    }

    public long getSeed() {
        return seed;
    }

    public void setSeed(long seed) {
        this.seed = seed;
    }

    public String getStrategy() {
        return strategy;
    }

    public void setStrategy(String strategy) {
        this.strategy = strategy;
    }

    public int getNumTopics() {
        return numTopics;
    }

    public void setNumTopics(int numTopics) {
        this.numTopics = numTopics;
    }

    public int getFmNumFactors() {
        return fmNumFactors;
    }

    public void setFmNumFactors(int fmNumFactors) {
        this.fmNumFactors = fmNumFactors;
    }

    public String getContextFormat() {
        return contextFormat;
    }

    public void setContextFormat(String contextFormat) {
        this.contextFormat = contextFormat;
    }

    public String getDataset() {
        return dataset;
    }

    public void setDataset(String dataset) {
        this.dataset = dataset;
    }

    @Override
    public String toString() {
        return "Properties{" +
                "crossValidationNumFolds=" + crossValidationNumFolds +
                ", topN=" + topN +
                ", topnNumItems=" + topnNumItems +
                ", relevanceThreshold=" + relevanceThreshold +
                ", seed=" + seed +
                ", strategy='" + strategy + '\'' +
                ", numTopics='" + numTopics + '\'' +
                ", fmNumFactors='" + fmNumFactors + '\'' +
                ", contextFormat='" + contextFormat + '\'' +
                ", dataset='" + dataset + '\'' +
                '}';
    }


    public static void main(String[] args) throws IOException {

        String fileName =
                "/Users/fpena/UCC/Thesis/projects/yelp/source/python/" +
                        "properties.yaml";
        loadProperties(fileName);
    }
}
