<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
        xmlns="http://www.w3.org/1999/XSL/Transform"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:fn="http://www.w3.org/2005/xpath-functions"
        xmlns:xs="http://www.w3.org/2001/XMLSchema"
        xmlns:="http://www.w3.org/2001/XMLSchema"
        version="2.0"
        exclude-result-prefixes="xs"
        >
    <xsoutput indent="yes"/>
    <param name="hId" as="xs:string" required="yes"/>
    <variable name="DEFVAL" as="xs:string" select="'DEFVAL'"/>
    <param name="outlineURI" as="xs:string" required="no" select="$DEFVAL"/>
    <param name="printMasterURI" as="xs:string" required="no" select="$DEFVAL"/>
    <template match="property[@name='alephID']">
        <copy>
            <apply-templates select="@*"/>

            <attribute name="value">
                <value-of select="$hId"/>
            </attribute>
        </copy>
    </template>
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

    <template match="property[@name='harvardMetadataLinks']">
        <copy>
            <apply-templates select="@*"/>
            <attribute name="value">
                <value-of select="replace(@value, 'hollis-id', $hId)"/>
            </attribute>
        </copy>
    </template>
    <template match="metadataCategory[@name='objectMetadata']">
         <copy>
        <apply-templates select="@*"/>
            <if test="fn:upper-case($printMasterURI) != $DEFVAL">
                <property name="relatedLinks" value="Relationship=Print Master --- URI={$printMasterURI}"/>
                         </if>
                </copy>
             <!--<xsl:copy>-->
                 <!--<xsl:text disable-output-escaping="no">&lt;property name="relatedLinks" value="Relationship=Print Master -&#45;&#45; URI=$printMasterURI"/&gt;-->
                 <!--</xsl:text>-->
             <!--</xsl:copy>-->
                <!--<xsl:copy>-->
                <!--<xsl:element name="property">-->
                    <!--<xsl:attribute name="name">relatedLinks</xsl:attribute>-->
                    <!--<xsl:attribute name="value">Relationship=Print Master -&#45;&#45; URI=<xsl:value-of select="$printMasterURI"/></xsl:attribute>-->
                <!--</xsl:element>-->
             <!--</xsl:copy>-->

            <!--<xsl:if test="fn:upper-case($outlineURI) != $DEFVAL">-->
              <!--<xsl:copy>-->
                  <!--<property name="relatedLinks" value=fn:concat('"Relationship=Outline -&#45;&#45; URI=',$outlineURI,'"')/>-->
              <!--</xsl:copy>-->
            <!--</xsl:if>-->
    </template>


    <template match="@*|node()">
        <copy>
            <apply-templates select="@*|node()"/>
        </copy>
    </template>
</xsl:stylesheet>
