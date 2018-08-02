<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0"
        xmlns:fn="http://www.w3.org/2005/xpath-functions">
    <xsl:param name="hId" as="xs:string" required="yes"/>
    <xsl:param name="DEFVAL" as="xs:string" required="no" select="'DEFVAL'"/>
    <xsl:param name="outlineURI" as="xs:string" required="no" select="$DEFVAL"/>
    <xsl:param name="printMasterURI" as="xs:string" required="no" select="$DEFVAL"/>
    <xsl:template match="property[@name='alephID']">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>

            <xsl:attribute name="value">
                <xsl:value-of select="$hId"/>
            </xsl:attribute>
        </xsl:copy>
    </xsl:template>
    <!--
     jimk: we dont look for existing, we have to add it if needed
    <xsl:template match="property[@name='printMasterLink']">
        <xsl:if test="fn:upper-case($printMasterOSN) != $DEFVAL" >
            <xsl:copy>
                <xsl:apply-templates select="@*"/>
                <xsl:attribute name="value">
                    <xsl:value-of select="replace(@value, 'printmaster-osn', $printMasterOSN)"/>
                </xsl:attribute>
            </xsl:copy>
        </xsl:if>
        </xsl:template>

     <xsl:template match="property[@name='outlineLink']">
        <xsl:if test="fn:upper-case($outlineOSN) != $DEFVAL ">
         <xsl:copy>
                <xsl:apply-templates select="@*"/>
                <xsl:attribute name="value">
                    <xsl:value-of select="replace(@value, 'outline-osn', $outlineOSN)"/>
                </xsl:attribute>
            </xsl:copy>
        </xsl:if>
        </xsl:template>-->

    <xsl:template match="property[@name='harvardMetadataLinks']">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:attribute name="value">
                <xsl:value-of select="replace(@value, 'hollis-id', $hId)"/>
            </xsl:attribute>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="metadataCategory[@name='objectMetadata']">
        <xsl:copy>
            <xsl:if test="fn:upper-case($printMasterURI) != $DEFVAL">
                <property name="relatedLinks" value="Relationship=Print Master --- URI=$printMasterURI"/>
            </xsl:if>
            <xsl:if test="fn:upper-case($outlineURI) != $DEFVAL">
                <property name="relatedLinks" value="Relationship=Outline --- URI=$outlineURI"/>
            </xsl:if>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>
