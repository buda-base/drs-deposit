<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                exclude-result-prefixes="xs"
                version="2.0">
    <xsl:output indent="yes"/>
    <xsl:param name="hId" as="xs:string" required="yes"/>
    <xsl:variable name="DEFVAL" as="xs:string" select="'DEFVAL'"/>
    <xsl:param name="outlineURI" as="xs:string" required="no"/>
    <xsl:param name="printMasterURI" as="xs:string" required="no"/>
    <!--<xsl:param name="outlineURI" as="xs:string" required="no" select="$DEFVAL"/>-->
    <!--<xsl:param name="printMasterURI" as="xs:string" required="no" select="$DEFVAL"/>-->
    <xsl:template match="property[@name='alephID']">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:attribute name="value">
                <xsl:value-of select="$hId"/>
            </xsl:attribute>
        </xsl:copy>
    </xsl:template>
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
            <xsl:apply-templates select="@*"/>
            <xsl:if test="$printMasterURI != '' ">

                <property name="relatedLinks" value="Relationship=Print Master --- URI={$printMasterURI}"/>
            </xsl:if>
            <xsl:if test="$outlineURI != '' ">
                <property name="relatedLinks" value="Relationship=Outline --- URI={$outlineURI}"/>
            </xsl:if>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>
